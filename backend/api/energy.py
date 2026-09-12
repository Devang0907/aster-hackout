from fastapi import APIRouter
from services.json_api import get_resource

router = APIRouter(
    prefix="/api/energy",
    tags=["Energy"]
)


@router.get("/")
async def get_energy():
    return await get_resource("energy_usage")
