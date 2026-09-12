from fastapi import APIRouter, HTTPException

from services.recommendation_service import (
    generate_factory_recommendations,
    create_recommendations_for_factory
)

router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


@router.get("/{factory_id}")
async def get_recommendations(factory_id: str):
    try:
        return await generate_factory_recommendations(factory_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("/{factory_id}/generate")
async def generate_recommendations(factory_id: str):
    try:
        return await create_recommendations_for_factory(factory_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )