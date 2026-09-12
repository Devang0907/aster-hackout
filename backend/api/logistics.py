from fastapi import APIRouter
from services.json_api import get_resource

router = APIRouter(
    prefix="/api/logistics",
    tags=["Logistics"]
)


@router.get("/")
async def get_logistics():
    return await get_resource("logistics")
