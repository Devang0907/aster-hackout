import argparse
import asyncio
import os
import sys
from datetime import datetime
from decimal import Decimal

from prisma import Prisma

sys.path.insert(0, str(__file__).split("prisma")[0].rstrip("\\/"))
from app.security.passwords import hash_password

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
]

ALTERNATIVES = [
    ("MAT-VPOLY", "MAT-RPOLY"),
    ("MAT-VPOLY", "MAT-RNYLON"),
    ("MAT-COTTON", "MAT-OCOTTON"),
    ("MAT-NYLON", "MAT-RNYLON"),
    ("MAT-STEEL", "MAT-RSTEEL"),
    ("MAT-ALUMINUM", "MAT-RALUMINUM"),
    ("MAT-PLASTIC", "MAT-RPLASTIC"),
]

INTERVENTIONS = [
    ("Solar Installation", "energy"),
    ("Energy Efficiency", "energy"),
    ("Recycled Material Substitution", "materials"),
    ("Waste Recovery", "waste"),
    ("Electrification", "process"),
    ("Process Optimization", "process"),
    ("Water Recycling", "water"),
    ("Material Reuse", "materials"),
    ("Packaging Reduction", "packaging"),
]

# Deliberately obvious demo values. They are not official, verified, certified,
# or suitable for regulatory reporting.
DEMO_EMISSION_FACTORS = [
    ("energy", "grid electricity", Decimal("0.70000000"), "kgCO2e/kWh"),
    ("fuel", "diesel combustion", Decimal("2.68000000"), "kgCO2e/litre"),
    ("transport", "road freight", Decimal("0.10000000"), "kgCO2e/tonne-km"),
]

DEMO_ADMIN_ID = "00000000-0000-0000-0000-000000000001"
DEMO_OWNER_ID = "00000000-0000-0000-0000-000000000002"
DEMO_MANAGER_ID = "00000000-0000-0000-0000-000000000003"
DEMO_FACTORY_ID = "00000000-0000-0000-0000-000000000010"
DEMO_PERIOD_ID = "00000000-0000-0000-0000-000000000020"
DEMO_OWNER_EMAIL = "demo-owner@example.com"
DEMO_MANAGER_EMAIL = "demo-manager@example.com"
DEMO_ADMIN_EMAIL = "demo-admin@example.com"
DEMO_ADMIN_PASSWORD = os.getenv("DEMO_ADMIN_PASSWORD", "Admin@12345")


async def seed_demo_tenant(database: Prisma, material_ids: dict[str, str]) -> None:
    await database.user.upsert(
        where={"id": DEMO_ADMIN_ID},
        data={
            "create": {
                "id": DEMO_ADMIN_ID,
                "fullName": "Demo Platform Admin",
                "email": DEMO_ADMIN_EMAIL,
                "passwordHash": hash_password(DEMO_ADMIN_PASSWORD),
                "role": "admin",
            },
            "update": {"isActive": True, "passwordHash": hash_password(DEMO_ADMIN_PASSWORD)},
        },
    )
    await database.user.upsert(
        where={"id": DEMO_OWNER_ID},
        data={
            "create": {
                "id": DEMO_OWNER_ID,
                "fullName": "Demo Factory Owner",
                "email": DEMO_OWNER_EMAIL,
                "role": "factory_owner",
            },
            "update": {"isActive": True},
        },
    )
    await database.user.upsert(
        where={"id": DEMO_MANAGER_ID},
        data={
            "create": {
                "id": DEMO_MANAGER_ID,
                "fullName": "Demo Factory Manager",
                "email": DEMO_MANAGER_EMAIL,
                "role": "factory_manager",
            },
            "update": {"isActive": True},
        },
    )
    await database.factory.upsert(
        where={"id": DEMO_FACTORY_ID},
        data={
            "create": {
                "id": DEMO_FACTORY_ID,
                "ownerId": DEMO_OWNER_ID,
                "managerId": DEMO_MANAGER_ID,
                "name": "Demo Circular Textiles Plant",
                "industryType": "Textiles",
                "description": "Removable demo tenant for local and staging verification.",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "country": "India",
                "employees": 120,
                "productionCapacity": Decimal("50000"),
                "productionUnit": "tonnes/year",
                "establishedYear": 2018,
            },
            "update": {"isActive": True, "managerId": DEMO_MANAGER_ID},
        },
    )
    await database.reportingperiod.upsert(
        where={"id": DEMO_PERIOD_ID},
        data={
            "create": {
                "id": DEMO_PERIOD_ID,
                "factoryId": DEMO_FACTORY_ID,
                "periodStart": datetime(2026, 1, 1),
                "periodEnd": datetime(2026, 1, 31),
                "status": "draft",
            },
            "update": {},
        },
    )

    records = [
        (
            database.factorymaterialusage,
            {"factoryId": DEMO_FACTORY_ID, "reportingPeriodId": DEMO_PERIOD_ID},
            {
                "factoryId": DEMO_FACTORY_ID,
                "reportingPeriodId": DEMO_PERIOD_ID,
                "materialId": material_ids["MAT-VPOLY"],
                "quantity": Decimal("1200"),
                "unit": "kg",
                "recycledPercentage": Decimal("25"),
                "supplierName": "Demo Fibre Supplier",
            },
        ),
        (
            database.energyusage,
            {"factoryId": DEMO_FACTORY_ID, "reportingPeriodId": DEMO_PERIOD_ID},
            {
                "factoryId": DEMO_FACTORY_ID,
                "reportingPeriodId": DEMO_PERIOD_ID,
                "energyType": "electricity",
                "quantity": Decimal("18000"),
                "unit": "kWh",
                "renewablePercentage": Decimal("35"),
                "source": "grid and rooftop solar",
            },
        ),
        (
            database.wastestream,
            {"factoryId": DEMO_FACTORY_ID, "reportingPeriodId": DEMO_PERIOD_ID},
            {
                "factoryId": DEMO_FACTORY_ID,
                "reportingPeriodId": DEMO_PERIOD_ID,
                "wasteType": "textile offcuts",
                "quantity": Decimal("100"),
                "unit": "kg",
                "treatmentMethod": "recovery",
                "recycledQuantity": Decimal("70"),
                "recoveredQuantity": Decimal("20"),
                "disposedQuantity": Decimal("10"),
            },
        ),
        (
            database.logistics,
            {"factoryId": DEMO_FACTORY_ID, "reportingPeriodId": DEMO_PERIOD_ID},
            {
                "factoryId": DEMO_FACTORY_ID,
                "reportingPeriodId": DEMO_PERIOD_ID,
                "transportType": "raw material delivery",
                "mode": "road",
                "distanceKm": Decimal("240"),
                "weightTonnes": Decimal("1.2"),
                "trips": 2,
                "fuelType": "diesel",
            },
        ),
    ]
    for delegate, where, data in records:
        if await delegate.find_first(where=where) is None:
            await delegate.create(data=data)


async def cleanup_demo_tenant(database: Prisma) -> None:
    for delegate in (
        database.factorymaterialusage,
        database.energyusage,
        database.wastestream,
        database.logistics,
    ):
        await delegate.delete_many(where={"factoryId": DEMO_FACTORY_ID})
    await database.reportingperiod.delete_many(where={"factoryId": DEMO_FACTORY_ID})
    await database.factory.delete_many(where={"id": DEMO_FACTORY_ID})
    await database.user.delete_many(
        where={"id": {"in": [DEMO_ADMIN_ID, DEMO_OWNER_ID, DEMO_MANAGER_ID]}}
    )


async def seed(include_demo_tenant: bool = False) -> None:
    database = Prisma()
    await database.connect()
    try:
        material_ids: dict[str, str] = {}
        for code, name, material_type, recycled, recyclable, score in MATERIALS:
            material = await database.material.upsert(
                where={"materialCode": code},
                data={
                    "create": {
                        "materialCode": code,
                        "name": name,
                        "materialType": material_type,
                        "category": material_type,
                        "recycledContentPossible": recycled,
                        "recyclable": recyclable,
                        "sustainabilityScore": score,
                    },
                    "update": {
                        "name": name,
                        "materialType": material_type,
                        "recycledContentPossible": recycled,
                        "recyclable": recyclable,
                        "sustainabilityScore": score,
                    },
                },
            )
            material_ids[code] = material.id

        for source_code, alternative_code in ALTERNATIVES:
            source_id = material_ids[source_code]
            alternative_id = material_ids[alternative_code]
            existing = await database.materialalternative.find_first(
                where={
                    "materialId": source_id,
                    "alternativeMaterialId": alternative_id,
                }
            )
            if existing is None:
                await database.materialalternative.create(
                    data={
                        "materialId": source_id,
                        "alternativeMaterialId": alternative_id,
                        "notes": (
                            "Example alternative; validate suitability for the actual process."
                        ),
                    }
                )

        for name, category in INTERVENTIONS:
            existing = await database.intervention.find_first(where={"name": name})
            if existing is None:
                await database.intervention.create(
                    data={
                        "name": name,
                        "category": category,
                        "description": (
                            "Seeded example intervention. Site-specific engineering and "
                            "financial validation is required before implementation."
                        ),
                    }
                )

        for category, activity, factor, unit in DEMO_EMISSION_FACTORS:
            existing = await database.emissionfactor.find_first(
                where={
                    "category": category,
                    "activity": activity,
                    "version": "demo-v1",
                }
            )
            if existing is None:
                await database.emissionfactor.create(
                    data={
                        "category": category,
                        "activity": activity,
                        "factor": factor,
                        "unit": unit,
                        "source": "DEMO/EXAMPLE DATA — NOT AN OFFICIAL EMISSION FACTOR",
                        "country": "India",
                        "version": "demo-v1",
                        "uncertaintyPercentage": Decimal("100"),
                    }
                )
        if include_demo_tenant:
            await seed_demo_tenant(database, material_ids)
    finally:
        await database.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed reference and optional demo data.")
    parser.add_argument(
        "--demo-tenant",
        action="store_true",
        help="also create the removable demo users, factory, period, and operational records",
    )
    parser.add_argument(
        "--cleanup-demo",
        action="store_true",
        help="remove the demo tenant without removing reference data",
    )
    args = parser.parse_args()
    if args.cleanup_demo:
        async def cleanup() -> None:
            database = Prisma()
            await database.connect()
            try:
                await cleanup_demo_tenant(database)
            finally:
                await database.disconnect()

        asyncio.run(cleanup())
    else:
        asyncio.run(seed(include_demo_tenant=args.demo_tenant))
