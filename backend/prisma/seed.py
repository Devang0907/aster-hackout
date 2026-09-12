import argparse
import asyncio
import os
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from prisma import Prisma

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_ROOT.parent
for import_path in (BACKEND_ROOT, REPOSITORY_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from app.security.passwords import hash_password
from recommendation_engine.data.interventions import INTERVENTIONS as ENGINE_INTERVENTIONS

MATERIALS = [
    ("MAT-VPOLY", "Virgin Polyester", "Polymer", False, True, Decimal("35")),
    ("MAT-RPOLY", "Recycled Polyester", "Polymer", True, True, Decimal("75")),
    ("MAT-COTTON", "Cotton", "Natural fibre", False, True, Decimal("55")),
    ("MAT-OCOTTON", "Organic Cotton", "Natural fibre", False, True, Decimal("75")),
    ("MAT-NYLON", "Nylon", "Polymer", False, True, Decimal("35")),
    ("MAT-RNYLON", "Recycled Nylon", "Polymer", True, True, Decimal("75")),
    ("MAT-STEEL", "Steel", "Metal", False, True, Decimal("55")),
    ("MAT-RSTEEL", "Recycled Steel", "Metal", True, True, Decimal("80")),
    ("MAT-ALUMINUM", "Aluminum", "Metal", False, True, Decimal("45")),
    ("MAT-RALUMINUM", "Recycled Aluminum", "Metal", True, True, Decimal("85")),
    ("MAT-PLASTIC", "Plastic", "Polymer", False, True, Decimal("30")),
    ("MAT-RPLASTIC", "Recycled Plastic", "Polymer", True, True, Decimal("70")),
    ("MAT-STEEL-001", "Steel", "Metal", True, True, Decimal("55")),
]

# Keep the supplied test material isolated from the shared catalog. The seeder
# must not invent or overwrite factors used by other factories.
MATERIAL_CARBON_FACTORS = {
    "MAT-STEEL-001": Decimal("1.85"),
}

ALTERNATIVES = [
    ("MAT-VPOLY", "MAT-RPOLY"),
    ("MAT-VPOLY", "MAT-RNYLON"),
    ("MAT-COTTON", "MAT-OCOTTON"),
    ("MAT-NYLON", "MAT-RNYLON"),
    ("MAT-STEEL", "MAT-RSTEEL"),
    ("MAT-ALUMINUM", "MAT-RALUMINUM"),
    ("MAT-PLASTIC", "MAT-RPLASTIC"),
]

# These values reproduce the supplied FullBackend/Context.md result. They are
# synthetic demo inputs, not verified factors for regulatory reporting.
DEMO_EMISSION_FACTORS = [
    ("energy", "electricity", Decimal("0.28000000"), "kgCO2e/kWh"),
    ("fuel", "diesel", Decimal("2.68000000"), "kgCO2e/litre"),
    ("transport", "diesel truck", Decimal("0.10000000"), "kgCO2e/tonne-km"),
    ("waste", "industrial waste", Decimal("0.50000000"), "kgCO2e/kg"),
]
DEMO_FACTOR_VERSION = "carbonwise-demo-v1"

DEMO_OWNER_ID = "39f9cb32-8f69-4650-bb95-aacf6e921c69"
DEMO_FACTORY_ID = "963b9cdf-7c11-48d6-98b0-904dbfe6b613"
DEMO_PERIOD_ID = "e3866bf8-246b-4f31-bf05-b62128ab9f9e"
DEMO_MATERIAL_ID = "6515de97-e5f9-4b31-beb8-6d0a3ea96ca2"
DEMO_OWNER_EMAIL = "carbonwise-demo@example.com"
DEMO_OWNER_PASSWORD = os.getenv("CARBONWISE_DEMO_PASSWORD", "CarbonWiseDemo@2026")
EXPECTED_DEMO_RESULT = {
    "totalCo2e": Decimal("383000"),
    "electricityCo2e": Decimal("35000"),
    "fuelCo2e": Decimal("0"),
    "materialCo2e": Decimal("92500"),
    "transportCo2e": Decimal("255000"),
    "wasteCo2e": Decimal("500"),
    "renewableOffset": Decimal("0"),
    "netCo2e": Decimal("383000"),
    "carbonIntensity": Decimal("38.3"),
}
EXPECTED_CALCULATION_VERSION = "1.0"
EXPECTED_MODEL_VERSION = "fullbackend-random-forest-1.0"


def _stable_id(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"carbonwise-demo:{name}"))


async def seed_reference_data(database: Prisma) -> dict[str, str]:
    material_ids: dict[str, str] = {}
    for code, name, material_type, recycled, recyclable, score in MATERIALS:
        material_data: dict[str, Any] = {
            "name": name,
            "materialType": material_type,
            "category": material_type,
            "recycledContentPossible": recycled,
            "recyclable": recyclable,
            "sustainabilityScore": score,
            "isActive": True,
        }
        carbon_factor = MATERIAL_CARBON_FACTORS.get(code)
        if carbon_factor is not None:
            material_data.update(
                {
                    "carbonFactor": carbon_factor,
                    "carbonUnit": "kgCO2e/kg",
                    "carbonFactorSource": (
                        "DEMO/EXAMPLE DATA — NOT AN OFFICIAL EMISSION FACTOR"
                    ),
                    "carbonFactorVersion": DEMO_FACTOR_VERSION,
                }
            )
        create_data = {"materialCode": code, **material_data}
        if code == "MAT-STEEL-001":
            create_data["id"] = DEMO_MATERIAL_ID
        material = await database.material.upsert(
            where={"materialCode": code},
            data={"create": create_data, "update": material_data},
        )
        material_ids[code] = material.id

    for source_code, alternative_code in ALTERNATIVES:
        source_id = material_ids[source_code]
        alternative_id = material_ids[alternative_code]
        existing = await database.materialalternative.find_first(
            where={"materialId": source_id, "alternativeMaterialId": alternative_id}
        )
        if existing is None:
            await database.materialalternative.create(
                data={
                    "materialId": source_id,
                    "alternativeMaterialId": alternative_id,
                    "notes": "Example alternative; validate suitability for the actual process.",
                }
            )

    for engine_key, template in ENGINE_INTERVENTIONS.items():
        existing = await database.intervention.find_first(
            where={"interventionType": engine_key}
        )
        if existing is None:
            existing = await database.intervention.find_first(where={"name": template["name"]})
        payback_months = Decimal(str(template["cost"])) / Decimal(
            str(template["savings"])
        ) * 12
        intervention_data = {
            "name": template["name"],
            "category": template["category"],
            "description": template["description"],
            "interventionType": engine_key,
            "estimatedCostMin": Decimal(str(template["cost"])),
            "estimatedCostMax": Decimal(str(template["cost"])),
            "expectedCo2ReductionPercentage": Decimal(
                str(template["co2_reduction_rate"] * 100)
            ),
            "paybackMonthsMin": payback_months,
            "paybackMonthsMax": payback_months,
            "feasibilityScore": Decimal(str(template["feasibility"] * 100)),
            "implementationComplexity": "demo-estimate",
        }
        if existing is None:
            await database.intervention.create(
                data={"id": _stable_id(f"intervention:{engine_key}"), **intervention_data}
            )
        else:
            await database.intervention.update(
                where={"id": existing.id}, data=intervention_data
            )

    for category, activity, factor, unit in DEMO_EMISSION_FACTORS:
        existing = await database.emissionfactor.find_first(
            where={
                "category": category,
                "activity": activity,
                "version": DEMO_FACTOR_VERSION,
            }
        )
        if existing is not None:
            if Decimal(str(existing.factor)) != factor:
                raise RuntimeError(
                    f"immutable demo factor {category}/{activity} has an unexpected value"
                )
            continue
        await database.emissionfactor.create(
            data={
                "id": _stable_id(f"factor:{category}:{activity}:{DEMO_FACTOR_VERSION}"),
                "category": category,
                "activity": activity,
                "factor": factor,
                "unit": unit,
                "source": "DEMO/EXAMPLE DATA — NOT AN OFFICIAL EMISSION FACTOR",
                "country": "India",
                "version": DEMO_FACTOR_VERSION,
                "uncertaintyPercentage": Decimal("100"),
            }
        )
    return material_ids


async def seed_demo_owner(
    database: Prisma,
    email: str = DEMO_OWNER_EMAIL,
    password: str = DEMO_OWNER_PASSWORD,
    *,
    reset_existing_password: bool = False,
) -> tuple[Any, bool]:
    normalized_email = email.strip().lower()
    owner = await database.user.find_unique(where={"email": normalized_email})
    created = owner is None
    if owner is None:
        owner_id = (
            DEMO_OWNER_ID
            if normalized_email == DEMO_OWNER_EMAIL
            else _stable_id(f"owner:{normalized_email}")
        )
        conflicting_id = await database.user.find_unique(where={"id": owner_id})
        if conflicting_id is not None:
            raise RuntimeError(
                f"demo owner id {owner_id} already belongs to another email address"
            )
        owner = await database.user.create(
            data={
                "id": owner_id,
                "fullName": "CarbonWise Demo Owner",
                "email": normalized_email,
                "passwordHash": hash_password(password),
                "role": "factory_owner",
                "isActive": True,
            }
        )
    else:
        role = str(getattr(owner.role, "value", owner.role))
        if role != "factory_owner":
            raise RuntimeError("the selected demo user must have the factory_owner role")
        update_data: dict[str, Any] = {"isActive": True}
        if reset_existing_password:
            update_data["passwordHash"] = hash_password(password)
        owner = await database.user.update(where={"id": owner.id}, data=update_data)
    return owner, created


async def _upsert_single_activity(
    delegate: Any, where: dict[str, Any], activity_id: str, data: dict[str, Any]
) -> None:
    existing = await delegate.find_many(where=where)
    if len(existing) > 1:
        raise RuntimeError("the CarbonWise demo period contains duplicate activity rows")
    if existing:
        await delegate.update(where={"id": existing[0].id}, data=data)
    else:
        await delegate.create(data={"id": activity_id, **data})


async def seed_demo_tenant(
    database: Prisma, material_ids: dict[str, str], owner_id: str = DEMO_OWNER_ID
) -> tuple[Any, Any, Any | None]:
    factory_data = {
        "ownerId": owner_id,
        "name": "CarbonWise Demo Factory",
        "industryType": "Manufacturing",
        "description": "Synthetic industrial dataset used to verify the CarbonWise pipeline.",
        "address": "Demo industrial estate",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "employees": 250,
        "productionCapacity": Decimal("10000"),
        "productionUnit": "tonnes/year",
        "isActive": True,
    }
    factory = await database.factory.upsert(
        where={"id": DEMO_FACTORY_ID},
        data={"create": {"id": DEMO_FACTORY_ID, **factory_data}, "update": factory_data},
    )
    period = await database.reportingperiod.upsert(
        where={"id": DEMO_PERIOD_ID},
        data={
            "create": {
                "id": DEMO_PERIOD_ID,
                "factoryId": DEMO_FACTORY_ID,
                "periodStart": datetime(2026, 1, 1),
                "periodEnd": datetime(2026, 12, 31),
                "status": "draft",
            },
            "update": {},
        },
    )
    existing_result = await database.carbonresult.find_first(
        where={"reportingPeriodId": DEMO_PERIOD_ID}, order={"calculatedAt": "desc"}
    )
    if existing_result is not None:
        return factory, period, existing_result

    status = str(getattr(period.status, "value", period.status))
    if status != "draft":
        period = await database.reportingperiod.update(
            where={"id": DEMO_PERIOD_ID}, data={"status": "draft"}
        )

    common = {"factoryId": DEMO_FACTORY_ID, "reportingPeriodId": DEMO_PERIOD_ID}
    await _upsert_single_activity(
        database.factorymaterialusage,
        common,
        _stable_id("activity:material"),
        {
            **common,
            "materialId": material_ids["MAT-STEEL-001"],
            "quantity": Decimal("50000"),
            "unit": "kg",
            "recycledPercentage": Decimal("20"),
            "supplierName": "CarbonWise Demo Steel Supplier",
        },
    )
    await _upsert_single_activity(
        database.energyusage,
        common,
        _stable_id("activity:energy"),
        {
            **common,
            "energyType": "Electricity",
            "quantity": Decimal("125000"),
            "unit": "kWh",
            "renewablePercentage": Decimal("15"),
            "source": "Grid",
        },
    )
    await _upsert_single_activity(
        database.wastestream,
        common,
        _stable_id("activity:waste"),
        {
            **common,
            "wasteType": "Industrial Waste",
            "quantity": Decimal("1000"),
            "unit": "kg",
            "treatmentMethod": "mixed",
            "recycledQuantity": Decimal("500"),
            "recoveredQuantity": Decimal("200"),
            "disposedQuantity": Decimal("300"),
        },
    )
    await _upsert_single_activity(
        database.logistics,
        common,
        _stable_id("activity:logistics"),
        {
            **common,
            "transportType": "Truck",
            "mode": "road",
            "distanceKm": Decimal("850"),
            "weightTonnes": Decimal("120"),
            "trips": 25,
            "fuelType": "diesel",
        },
    )
    return factory, period, None


def validate_existing_demo_result(result: Any) -> None:
    mismatches = []
    for field, expected in EXPECTED_DEMO_RESULT.items():
        try:
            matches = Decimal(str(getattr(result, field))) == expected
        except Exception:
            matches = False
        if not matches:
            mismatches.append(field)
    if str(result.calculationVersion) != EXPECTED_CALCULATION_VERSION:
        mismatches.append("calculationVersion")
    if str(result.mlModelVersion) != EXPECTED_MODEL_VERSION:
        mismatches.append("mlModelVersion")
    if mismatches:
        joined = ", ".join(mismatches)
        raise RuntimeError(
            "the fixed demo period already has incompatible immutable output "
            f"({joined}); use a fresh demo database or new demo identifiers"
        )


async def seed(
    include_demo_tenant: bool = False,
    *,
    owner_email: str = DEMO_OWNER_EMAIL,
    owner_password: str | None = None,
    reset_existing_password: bool = False,
) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    configured_demo_password = (
        settings.carbonwise_demo_password.get_secret_value()
        if settings.carbonwise_demo_password is not None
        else None
    )
    effective_password = owner_password or configured_demo_password or DEMO_OWNER_PASSWORD
    if include_demo_tenant and settings.app_env == "production" and not configured_demo_password:
        raise RuntimeError(
            "CARBONWISE_DEMO_PASSWORD must be explicitly set before seeding production"
        )
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not configured")
    os.environ.setdefault("DATABASE_URL", settings.database_url.get_secret_value())
    database = Prisma()
    await database.connect()
    try:
        material_ids = await seed_reference_data(database)
        if include_demo_tenant:
            owner, owner_created = await seed_demo_owner(
                database,
                owner_email,
                effective_password,
                reset_existing_password=reset_existing_password,
            )
            factory, period, result = await seed_demo_tenant(database, material_ids, owner.id)
            if result is None:
                await database.reportingperiod.update(
                    where={"id": period.id},
                    data={
                        "status": "submitted",
                        "submittedById": owner.id,
                        "submittedAt": datetime.now(UTC),
                    },
                )
                from app.services.pipeline import run_reporting_period_pipeline

                result = await run_reporting_period_pipeline(
                    UUID(str(factory.id)), UUID(str(period.id)), database
                )
            else:
                validate_existing_demo_result(result)

            sources = await database.emissionsource.find_many(
                where={"resultId": result.id}, order={"rank": "asc"}
            )
            recommendations = await database.recommendation.find_many(
                where={"resultId": result.id}, order={"priority": "asc"}
            )
            print("CarbonWise industrial demo is ready")
            print(f"Owner: {owner.email} ({'created' if owner_created else 'linked'})")
            print(f"Factory ID: {factory.id}")
            print(f"Reporting period ID: {period.id}")
            print(f"Carbon result ID: {result.id}")
            print(f"Net emissions: {Decimal(str(result.netCo2e)):.2f} kgCO2e")
            print(f"Emission sources: {len(sources)}")
            print(f"Recommendations: {len(recommendations)}")
            if owner_created or reset_existing_password:
                print("Sign-in password: CARBONWISE_DEMO_PASSWORD (or the documented dev default)")
            elif not owner.passwordHash:
                print(
                    "Existing owner has no password; rerun with --reset-existing-password "
                    "and CARBONWISE_DEMO_PASSWORD set"
                )
    finally:
        await database.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed reference and optional demo data.")
    parser.add_argument(
        "--demo-tenant",
        action="store_true",
        help="create, calculate, and persist the linked CarbonWise industrial demo",
    )
    parser.add_argument(
        "--user-email",
        default=DEMO_OWNER_EMAIL,
        help="factory-owner email to create or link (default: carbonwise-demo@example.com)",
    )
    parser.add_argument(
        "--reset-existing-password",
        action="store_true",
        help="replace an existing demo owner's password from CARBONWISE_DEMO_PASSWORD",
    )
    args = parser.parse_args()
    asyncio.run(
        seed(
            include_demo_tenant=args.demo_tenant,
            owner_email=args.user_email,
            owner_password=None,
            reset_existing_password=args.reset_existing_password,
        )
    )
