from services.data_api import (
    get_resource,
    get_resource_by_id,
    create_resource,
    update_resource
)

from recommendation_engine.main import (
    run_recommendation_engine
)


# --------------------------------------------------
# ML intervention -> database intervention
#
# Your ML engine uses string IDs such as:
# transport_optimization
#
# Your database uses UUIDs.
#
# For now we match ML interventions to your existing
# database interventions by name.
# --------------------------------------------------

ML_TO_DB_INTERVENTION = {

    # Electricity
    "renewable_electricity":
        "Solar Power Installation",

    "energy_efficiency":
        "Energy Efficiency Upgrade",

    "smart_energy_management":
        "Energy Efficiency Upgrade",

    # Fuel
    "fuel_efficiency":
        "Diesel Usage Reduction",

    "fuel_switching":
        "Diesel Usage Reduction",

    # Materials
    "recycled_material":
        "Recycled Steel Substitution",

    "material_efficiency":
        "Recycled Steel Substitution",

    "sustainable_material_substitution":
        "Recycled Steel Substitution",

    # Transport
    "transport_optimization":
        "Logistics Route Optimization",

    "electric_transport":
        "Logistics Route Optimization",

    # Waste
    "waste_recovery":
        "Waste Recycling Improvement",

    "waste_recycling":
        "Waste Recycling Improvement",

    "industrial_symbiosis":
        "Waste Recycling Improvement"
}


# --------------------------------------------------
# ML source names -> database emission source types
# --------------------------------------------------

ENGINE_SOURCE_TO_DB = {
    "electricity": "energy",
    "diesel": "fuel",
    "raw_material": "material",
    "transport": "transport",
    "waste": "waste"
}


# --------------------------------------------------
# Get latest carbon result
# --------------------------------------------------

async def get_latest_carbon_result(factory_id: str):

    carbon_results = await get_resource(
        "carbon_results"
    )

    factory_results = [
        result
        for result in carbon_results
        if str(result["factory_id"]) == str(factory_id)
    ]

    if not factory_results:
        return None

    return max(
        factory_results,
        key=lambda x: str(x["calculated_at"])
    )


# --------------------------------------------------
# Build ML emission input
# --------------------------------------------------

def build_emissions(carbon_result):

    return {

        "electricity": float(
            carbon_result.get(
                "electricity_co2e"
            ) or 0
        ),

        "diesel": float(
            carbon_result.get(
                "fuel_co2e"
            ) or 0
        ),

        "raw_material": float(
            carbon_result.get(
                "material_co2e"
            ) or 0
        ),

        "waste": float(
            carbon_result.get(
                "waste_co2e"
            ) or 0
        ),

        "transport": float(
            carbon_result.get(
                "transport_co2e"
            ) or 0
        )
    }


# --------------------------------------------------
# Build ranked sources for recommendation engine
# --------------------------------------------------

def build_ranked_sources(emissions):

    ranked_sources = [

        {
            "source": source,
            "emission": emission
        }

        for source, emission
        in emissions.items()

        if emission > 0
    ]

    ranked_sources.sort(
        key=lambda x: x["emission"],
        reverse=True
    )

    return ranked_sources


# --------------------------------------------------
# GET existing recommendations
# --------------------------------------------------

async def generate_factory_recommendations(
    factory_id: str
):

    # --------------------------------------------------
    # Factory
    # --------------------------------------------------

    factory = await get_resource_by_id(
        "factories",
        factory_id
    )

    if not factory:
        raise ValueError(
            "Factory not found"
        )


    # --------------------------------------------------
    # Latest carbon result
    # --------------------------------------------------

    latest_result = (
        await get_latest_carbon_result(
            factory_id
        )
    )

    if not latest_result:

        return {
            "factory": factory,
            "emissions": {},
            "ranked_sources": [],
            "recommendations": []
        }


    result_id = str(
        latest_result["id"]
    )


    # --------------------------------------------------
    # Emissions
    # --------------------------------------------------

    emissions = build_emissions(
        latest_result
    )


    # --------------------------------------------------
    # DB emission sources
    # --------------------------------------------------

    all_sources = await get_resource(
        "emission_sources"
    )

    sources = [

        source

        for source in all_sources

        if str(
            source["result_id"]
        ) == result_id
    ]

    sources.sort(
        key=lambda x:
            x.get("rank", 999)
    )


    ranked_sources = [

        {
            "id":
                source["id"],

            "source":
                source["source_name"],

            "source_type":
                source["source_type"],

            "emission":
                source["emissions_co2e"],

            "percentage":
                source["percentage"],

            "severity":
                source["severity"],

            "rank":
                source["rank"]
        }

        for source in sources
    ]


    # --------------------------------------------------
    # Existing saved recommendations
    # --------------------------------------------------

    all_recommendations = await get_resource(
        "recommendations"
    )

    recommendations = [

        recommendation

        for recommendation
        in all_recommendations

        if (
            str(
                recommendation["factory_id"]
            )
            == str(factory_id)

            and

            str(
                recommendation["result_id"]
            )
            == result_id
        )
    ]


    recommendations.sort(
        key=lambda x:
            x.get("priority", 999)
    )


    # --------------------------------------------------
    # Intervention information
    # --------------------------------------------------

    interventions = await get_resource(
        "interventions"
    )

    intervention_map = {

        str(intervention["id"]):
            intervention

        for intervention
        in interventions
    }


    formatted_recommendations = []


    for recommendation in recommendations:

        intervention = (
            intervention_map.get(
                str(
                    recommendation[
                        "intervention_id"
                    ]
                ),
                {}
            )
        )

        formatted_recommendations.append({

            **recommendation,

            "name":
                intervention.get("name"),

            "category":
                intervention.get("category"),

            "description":
                intervention.get(
                    "description"
                ),

            "intervention_type":
                intervention.get(
                    "intervention_type"
                )
        })


    return {

        "factory":
            factory,

        "carbon_result":
            latest_result,

        "emissions":
            emissions,

        "ranked_sources":
            ranked_sources,

        "recommendations":
            formatted_recommendations
    }


# --------------------------------------------------
# CREATE / UPDATE ML recommendations
# --------------------------------------------------

async def create_recommendations_for_factory(
    factory_id: str
):

    # --------------------------------------------------
    # Latest carbon result
    # --------------------------------------------------

    latest_result = (
        await get_latest_carbon_result(
            factory_id
        )
    )

    if not latest_result:
        raise ValueError(
            "No carbon result found for this factory"
        )


    result_id = str(
        latest_result["id"]
    )


    # --------------------------------------------------
    # Build ML input
    # --------------------------------------------------

    emissions = build_emissions(
        latest_result
    )


    ranked_sources = build_ranked_sources(
        emissions
    )


    if not ranked_sources:

        return {
            "created_count": 0,
            "updated_count": 0,
            "created": [],
            "updated": [],
            "ml_recommendations": []
        }


    # --------------------------------------------------
    # RUN THE ACTUAL ML RECOMMENDATION ENGINE
    # --------------------------------------------------

    ml_recommendations = (
        run_recommendation_engine(
            emissions,
            ranked_sources
        )
    )


    # --------------------------------------------------
    # Database interventions
    # --------------------------------------------------

    interventions = await get_resource(
        "interventions"
    )


    interventions_by_name = {

        str(
            intervention.get("name")
        ).lower():
            intervention

        for intervention
        in interventions
    }


    # --------------------------------------------------
    # Database emission sources
    # --------------------------------------------------

    all_sources = await get_resource(
        "emission_sources"
    )


    result_sources = [

        source

        for source in all_sources

        if str(
            source["result_id"]
        ) == result_id
    ]


    sources_by_type = {

        str(
            source["source_type"]
        ).lower():
            source

        for source
        in result_sources
    }


    # --------------------------------------------------
    # Existing recommendations
    # --------------------------------------------------

    all_recommendations = await get_resource(
        "recommendations"
    )


    existing_recommendations = [

        recommendation

        for recommendation
        in all_recommendations

        if (
            str(
                recommendation["factory_id"]
            )
            == str(factory_id)

            and

            str(
                recommendation["result_id"]
            )
            == result_id
        )
    ]


    # --------------------------------------------------
    # Existing lookup
    #
    # Key:
    # intervention_id + emission_source_id
    # --------------------------------------------------

    existing_map = {

        (
            str(
                recommendation[
                    "intervention_id"
                ]
            ),

            str(
                recommendation[
                    "emission_source_id"
                ]
            )
        ):
            recommendation

        for recommendation
        in existing_recommendations

        if recommendation.get(
            "emission_source_id"
        )
    }


    created = []
    updated = []


    # --------------------------------------------------
    # Avoid duplicate DB mappings
    #
    # Some ML interventions currently map to the
    # same database intervention.
    # --------------------------------------------------

    processed_pairs = set()


    # --------------------------------------------------
    # Save ML recommendations
    # --------------------------------------------------

    for priority, recommendation in enumerate(
        ml_recommendations,
        start=1
    ):

        # ----------------------------------------------
        # ML intervention ID
        # ----------------------------------------------

        ml_intervention_id = (
            recommendation.get(
                "id"
            )
            or recommendation.get(
                "intervention_id"
            )
        )


        if not ml_intervention_id:
            continue


        # ----------------------------------------------
        # Find DB intervention
        # ----------------------------------------------

        db_intervention_name = (
            ML_TO_DB_INTERVENTION.get(
                ml_intervention_id
            )
        )


        if not db_intervention_name:
            continue


        db_intervention = (
            interventions_by_name.get(
                db_intervention_name.lower()
            )
        )


        if not db_intervention:
            continue


        # ----------------------------------------------
        # ML source
        # ----------------------------------------------

        engine_source = str(
            recommendation.get(
                "source"
            ) or ""
        ).lower()


        db_source_type = (
            ENGINE_SOURCE_TO_DB.get(
                engine_source
            )
        )


        if not db_source_type:
            continue


        emission_source = (
            sources_by_type.get(
                db_source_type
            )
        )


        if not emission_source:
            continue


        db_intervention_id = str(
            db_intervention["id"]
        )

        emission_source_id = str(
            emission_source["id"]
        )


        pair = (
            db_intervention_id,
            emission_source_id
        )


        # ----------------------------------------------
        # Prevent duplicate mapped recommendations
        # ----------------------------------------------

        if pair in processed_pairs:
            continue

        processed_pairs.add(
            pair
        )


        # ----------------------------------------------
        # ML predicted CO2 reduction
        # ----------------------------------------------

        predicted_reduction = float(
            recommendation.get(
                "predicted_co2_reduction"
            ) or 0
        )


        # ----------------------------------------------
        # Cost
        # ----------------------------------------------

        cost = float(
            recommendation.get(
                "cost"
            ) or 0
        )


        # ----------------------------------------------
        # Annual savings
        # ----------------------------------------------

        savings = float(
            recommendation.get(
                "savings"
            ) or 0
        )


        # ----------------------------------------------
        # ROI
        # ----------------------------------------------

        roi = float(
            recommendation.get(
                "roi"
            ) or 0
        )


        # ----------------------------------------------
        # Feasibility
        #
        # ML engine uses 0 -> 1.
        # Database uses 0 -> 100.
        # ----------------------------------------------

        feasibility = float(
            recommendation.get(
                "feasibility"
            ) or 0
        )


        feasibility_score = (
            feasibility * 100
            if feasibility <= 1
            else feasibility
        )


        # ----------------------------------------------
        # Recommendation score
        #
        # Engine generally returns 0 -> 1.
        # Store as percentage.
        # ----------------------------------------------

        score = float(
            recommendation.get(
                "score"
            ) or 0
        )


        recommendation_score = (
            score * 100
            if score <= 1
            else score
        )


        recommendation_score = min(
            max(
                recommendation_score,
                0
            ),
            100
        )


        # ----------------------------------------------
        # Payback
        # ----------------------------------------------

        payback_months = None


        if savings > 0:

            payback_months = (
                cost
                / savings
                * 12
            )


        # ----------------------------------------------
        # Explanation
        # ----------------------------------------------

        source_emission = float(
            emission_source.get(
                "emissions_co2e"
            ) or 0
        )


        source_percentage = float(
            emission_source.get(
                "percentage"
            ) or 0
        )


        explanation = (

            f"{emission_source['source_name']} "
            f"produces {source_emission:.2f} "
            f"kgCO2e "

            f"({source_percentage:.2f}% of total emissions). "

            f"The ML recommendation model predicts that "
            f"{recommendation.get('name', db_intervention_name)} "
            f"could reduce approximately "
            f"{predicted_reduction:.2f} kgCO2e. "

            f"Estimated implementation cost is "
            f"{cost:.2f}, with estimated annual savings "
            f"of {savings:.2f}. "

            f"Recommendation score: "
            f"{recommendation_score:.2f}/100."
        )


        # ----------------------------------------------
        # Recommendation database data
        # ----------------------------------------------

        recommendation_data = {

            "factory_id":
                factory_id,

            "result_id":
                result_id,

            "intervention_id":
                db_intervention_id,

            "emission_source_id":
                emission_source_id,

            "priority":
                priority,

            "recommendation_score":
                recommendation_score,

            "estimated_co2_reduction":
                predicted_reduction,

            "estimated_cost":
                cost,

            "estimated_annual_savings":
                savings,

            "payback_months":
                payback_months,

            "feasibility_score":
                feasibility_score,

            # For now this is not a real ML
            # probability/confidence measure.
            "confidence_score":
                85,

            "ai_explanation":
                explanation,

            "status":
                "new"
        }


        # ----------------------------------------------
        # Existing?
        # ----------------------------------------------

        existing = existing_map.get(
            pair
        )


        # ----------------------------------------------
        # UPDATE
        # ----------------------------------------------

        if existing:

            saved = await update_resource(
                "recommendations",
                str(existing["id"]),
                recommendation_data
            )

            updated.append(
                saved
            )


        # ----------------------------------------------
        # CREATE
        # ----------------------------------------------

        else:

            saved = await create_resource(
                "recommendations",
                recommendation_data
            )

            created.append(
                saved
            )


    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    return {

        "created_count":
            len(created),

        "updated_count":
            len(updated),

        "created":
            created,

        "updated":
            updated,

        # Very useful while testing.
        # This proves that the ML engine actually ran.
        "ml_recommendations":
            ml_recommendations
    }