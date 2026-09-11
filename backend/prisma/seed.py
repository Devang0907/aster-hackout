import asyncio
from decimal import Decimal

from prisma import Prisma

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


async def seed() -> None:
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
    finally:
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())
