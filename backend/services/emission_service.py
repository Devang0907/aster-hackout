from services.data_api import (
    get_resource,
    get_resource_by_id,
    create_resource,
    update_resource
)


async def calculate_factory_emissions(factory_id: str):

    # --------------------------------------------------
    # 1. Get factory
    # --------------------------------------------------

    factory = await get_resource_by_id(
        "factories",
        factory_id
    )

    if not factory:
        raise ValueError("Factory not found")


    # --------------------------------------------------
    # 2. Find latest reporting period
    # --------------------------------------------------

    periods = await get_resource("reporting_periods")

    factory_periods = [
        p for p in periods
        if str(p["factory_id"]) == str(factory_id)
    ]

    if not factory_periods:
        raise ValueError("No reporting period found")

    latest_period = max(
        factory_periods,
        key=lambda x: str(x["period_end"])
    )

    period_id = str(latest_period["id"])


    # --------------------------------------------------
    # 3. Load raw data
    # --------------------------------------------------

    energy_rows = await get_resource(
        "energy_usage"
    )

    waste_rows = await get_resource(
        "waste_streams"
    )

    logistics_rows = await get_resource(
        "logistics"
    )

    material_usage_rows = await get_resource(
        "factory_material_usage"
    )

    materials = await get_resource(
        "materials"
    )

    factors = await get_resource(
        "emission_factors"
    )


    # --------------------------------------------------
    # 4. Filter current factory + reporting period
    # --------------------------------------------------

    energy_rows = [
        row for row in energy_rows
        if (
            str(row["factory_id"]) == str(factory_id)
            and
            str(row["reporting_period_id"]) == period_id
        )
    ]

    waste_rows = [
        row for row in waste_rows
        if (
            str(row["factory_id"]) == str(factory_id)
            and
            str(row["reporting_period_id"]) == period_id
        )
    ]

    logistics_rows = [
        row for row in logistics_rows
        if (
            str(row["factory_id"]) == str(factory_id)
            and
            str(row["reporting_period_id"]) == period_id
        )
    ]

    material_usage_rows = [
        row for row in material_usage_rows
        if (
            str(row["factory_id"]) == str(factory_id)
            and
            str(row["reporting_period_id"]) == period_id
        )
    ]


    # --------------------------------------------------
    # 5. Helper maps
    # --------------------------------------------------

    material_map = {
        str(material["id"]): material
        for material in materials
    }

    factor_map = {
        (
            str(factor["category"]).lower(),
            str(factor["activity"]).lower()
        ): float(factor["factor"])
        for factor in factors
    }


    # --------------------------------------------------
    # 6. Electricity emissions
    # --------------------------------------------------

    electricity_co2e = 0.0

    for row in energy_rows:

        if (
            str(row["energy_type"]).lower()
            == "electricity"
        ):

            factor = factor_map.get(
                ("energy", "electricity"),
                0
            )

            quantity = float(
                row.get("quantity") or 0
            )

            electricity_co2e += (
                quantity * factor
            )


    # --------------------------------------------------
    # 7. Material emissions
    # --------------------------------------------------

    material_co2e = 0.0

    for usage in material_usage_rows:

        material = material_map.get(
            str(usage["material_id"])
        )

        if not material:
            continue

        factor = float(
            material.get("carbon_factor") or 0
        )

        quantity = float(
            usage.get("quantity") or 0
        )

        material_co2e += (
            quantity * factor
        )


    # --------------------------------------------------
    # 8. Transport emissions
    #
    # tonne-km = distance × weight × trips
    # --------------------------------------------------

    transport_co2e = 0.0

    transport_factor = factor_map.get(
        ("transport", "diesel truck"),
        0
    )

    for row in logistics_rows:

        distance = float(
            row.get("distance_km") or 0
        )

        weight = float(
            row.get("weight_tonnes") or 0
        )

        trips = float(
            row.get("trips") or 0
        )

        tonne_km = (
            distance
            * weight
            * trips
        )

        transport_co2e += (
            tonne_km
            * transport_factor
        )


    # --------------------------------------------------
    # 9. Waste emissions
    # --------------------------------------------------

    waste_co2e = 0.0

    for row in waste_rows:

        waste_type = str(
            row.get("waste_type") or ""
        ).lower()

        factor = factor_map.get(
            (
                "waste",
                waste_type
            ),
            0
        )

        quantity = float(
            row.get("quantity") or 0
        )

        waste_co2e += (
            quantity * factor
        )


    # --------------------------------------------------
    # 10. Fuel emissions
    #
    # No separate fuel_usage table currently
    # --------------------------------------------------

    fuel_co2e = 0.0


    # --------------------------------------------------
    # 11. Total emissions
    # --------------------------------------------------

    total_co2e = (
        electricity_co2e
        + fuel_co2e
        + material_co2e
        + transport_co2e
        + waste_co2e
    )


    # --------------------------------------------------
    # 12. Renewable offset
    # --------------------------------------------------

    renewable_offset = 0.0

    net_co2e = (
        total_co2e
        - renewable_offset
    )


    # --------------------------------------------------
    # 13. Carbon intensity
    #
    # total emissions / production capacity
    # --------------------------------------------------

    production_capacity = float(
        factory.get("production_capacity")
        or 0
    )

    if production_capacity > 0:

        carbon_intensity = (
            net_co2e
            / production_capacity
        )

    else:

        carbon_intensity = 0.0


    # --------------------------------------------------
    # 14. Find existing carbon result
    # --------------------------------------------------

    existing_results = await get_resource(
        "carbon_results"
    )

    existing_result = next(
        (
            result
            for result in existing_results
            if (
                str(
                    result["reporting_period_id"]
                ) == period_id
                and
                str(
                    result["calculation_version"]
                ) == "1.0"
            )
        ),
        None
    )


    # --------------------------------------------------
    # 15. Carbon result data
    # --------------------------------------------------

    result_data = {
        "factory_id":
            factory_id,

        "reporting_period_id":
            period_id,

        "total_co2e":
            total_co2e,

        "electricity_co2e":
            electricity_co2e,

        "fuel_co2e":
            fuel_co2e,

        "material_co2e":
            material_co2e,

        "transport_co2e":
            transport_co2e,

        "waste_co2e":
            waste_co2e,

        "renewable_offset":
            renewable_offset,

        "net_co2e":
            net_co2e,

        "carbon_intensity":
            carbon_intensity,

        "carbon_intensity_unit":
            "kgCO2e/unit",

        "calculation_version":
            "1.0"
    }


    # --------------------------------------------------
    # 16. Update existing result or create new result
    # --------------------------------------------------

    if existing_result:

        carbon_result = await update_resource(
            "carbon_results",
            str(existing_result["id"]),
            result_data
        )

    else:

        carbon_result = await create_resource(
            "carbon_results",
            result_data
        )


    # --------------------------------------------------
    # 17. Prepare emission sources
    # --------------------------------------------------

    source_data = [
        {
            "name": "Electricity",
            "type": "energy",
            "emission": electricity_co2e
        },
        {
            "name": "Fuel",
            "type": "fuel",
            "emission": fuel_co2e
        },
        {
            "name": "Raw Material",
            "type": "material",
            "emission": material_co2e
        },
        {
            "name": "Transport",
            "type": "transport",
            "emission": transport_co2e
        },
        {
            "name": "Waste",
            "type": "waste",
            "emission": waste_co2e
        }
    ]


    # --------------------------------------------------
    # 18. Sort largest emission source first
    # --------------------------------------------------

    source_data.sort(
        key=lambda x: x["emission"],
        reverse=True
    )


    # --------------------------------------------------
    # 19. Get existing emission sources
    # --------------------------------------------------

    all_existing_sources = await get_resource(
        "emission_sources"
    )

    existing_sources = [
        source
        for source in all_existing_sources
        if (
            str(source["result_id"])
            == str(carbon_result["id"])
        )
    ]

    existing_source_map = {
        str(
            source["source_type"]
        ).lower(): source

        for source in existing_sources
    }


    # --------------------------------------------------
    # 20. Temporarily move ranks
    #
    # Prevents UNIQUE(result_id, rank) conflicts
    # --------------------------------------------------

    temp_rank = 100

    for source in existing_sources:

        await update_resource(
            "emission_sources",
            str(source["id"]),
            {
                "rank": temp_rank
            }
        )

        temp_rank += 1


    # --------------------------------------------------
    # 21. Update/create emission sources
    # --------------------------------------------------

    saved_sources = []

    for rank, source in enumerate(
        source_data,
        start=1
    ):

        emission = float(
            source["emission"]
        )


        # ----------------------------------------------
        # Percentage
        # ----------------------------------------------

        if total_co2e > 0:

            percentage = (
                emission
                / total_co2e
            ) * 100

        else:

            percentage = 0.0


        # ----------------------------------------------
        # Severity
        # ----------------------------------------------

        if percentage >= 50:

            severity = "critical"

        elif percentage >= 20:

            severity = "high"

        elif percentage >= 5:

            severity = "medium"

        else:

            severity = "low"


        # ----------------------------------------------
        # Dynamic explanation
        # ----------------------------------------------

        explanation = (
            f"{source['name']} contributes "
            f"{emission:.2f} kgCO2e, which is "
            f"{percentage:.2f}% of total emissions."
        )


        # ----------------------------------------------
        # Values to save
        # ----------------------------------------------

        source_values = {
            "result_id":
                str(carbon_result["id"]),

            "source_name":
                source["name"],

            "source_type":
                source["type"],

            "emissions_co2e":
                emission,

            "percentage":
                percentage,

            "severity":
                severity,

            "rank":
                rank,

            "explanation":
                explanation
        }


        existing_source = (
            existing_source_map.get(
                source["type"].lower()
            )
        )


        # ----------------------------------------------
        # Update existing source
        # ----------------------------------------------

        if existing_source:

            saved_source = await update_resource(
                "emission_sources",
                str(existing_source["id"]),
                source_values
            )


        # ----------------------------------------------
        # Create missing source
        # ----------------------------------------------

        else:

            saved_source = await create_resource(
                "emission_sources",
                source_values
            )


        saved_sources.append(
            saved_source
        )


    # --------------------------------------------------
    # 22. Return result
    # --------------------------------------------------

    return {
        "factory_id":
            factory_id,

        "reporting_period_id":
            period_id,

        "carbon_result":
            carbon_result,

        "emission_sources":
            saved_sources
    }