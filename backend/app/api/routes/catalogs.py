from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.security.authentication import get_current_user
from app.services import catalogs as service

router = APIRouter(prefix="/catalogs", tags=["catalogs"])
Database = Annotated[Any, Depends(get_database)]
CurrentUser = Annotated[Any, Depends(get_current_user)]


@router.get("/materials")
async def materials(_: CurrentUser, database: Database) -> list[Any]:
    return await service.list_materials(database)


@router.get("/material-alternatives")
async def material_alternatives(_: CurrentUser, database: Database) -> list[Any]:
    return await service.list_material_alternatives(database)


@router.get("/interventions")
async def interventions(_: CurrentUser, database: Database) -> list[Any]:
    return await service.list_interventions(database)


@router.get("/emission-factors")
async def emission_factors(_: CurrentUser, database: Database) -> list[Any]:
    return await service.list_emission_factors(database)