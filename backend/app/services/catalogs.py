from typing import Any


async def list_materials(database: Any) -> list[Any]:
    return await database.material.find_many(
        where={"isActive": True}, order={"name": "asc"}
    )


async def list_material_alternatives(database: Any) -> list[Any]:
    return await database.materialalternative.find_many(
        include={"material": True, "alternativeMaterial": True},
        order={"createdAt": "desc"},
    )


async def list_interventions(database: Any) -> list[Any]:
    return await database.intervention.find_many(order={"name": "asc"})


async def list_emission_factors(database: Any) -> list[Any]:
    return await database.emissionfactor.find_many(order={"createdAt": "desc"})