# backend/api/recommendations.py

from fastapi import APIRouter, HTTPException
from services.recommendation_service import generate_factory_recommendations

router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)

@router.get("/{factory_id}")
async def get_recommendations(factory_id: str):
    try:
        return await generate_factory_recommendations(factory_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )