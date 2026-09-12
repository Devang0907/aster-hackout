from fastapi import APIRouter

from services.emission_service import (
    get_factory_emissions
)

router = APIRouter(
    prefix="/api/emissions",
    tags=["Emissions"]
)


@router.get("/{factory_id}")
async def get_emissions(factory_id: int):

    return await get_factory_emissions(
        factory_id
    )
