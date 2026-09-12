from fastapi import APIRouter

from services.simulation_service import (
    save_simulation
)

router = APIRouter(
    prefix="/api/simulations",
    tags=["Simulations"]
)


@router.post("/")
async def create_simulation(data: dict):

    return await save_simulation(data)
