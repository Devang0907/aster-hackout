from fastapi import APIRouter
from services.json_api import get_resource

router = APIRouter(
    prefix="/api/waste",
    tags=["Waste"]
)


@router.get("/")
async def get_waste():
    return await get_resource("waste_streams")
