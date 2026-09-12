from fastapi import APIRouter
from services.json_api import get_resource

router = APIRouter(
    prefix="/api/materials",
    tags=["Materials"]
)


@router.get("/")
async def get_materials():
    return await get_resource("materials")
