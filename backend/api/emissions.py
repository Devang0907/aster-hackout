from fastapi import APIRouter, HTTPException

from services.emission_service import (
    calculate_factory_emissions
)

from services.recommendation_service import (
    create_recommendations_for_factory
)


router = APIRouter(
    prefix="/api/emissions",
    tags=["Emissions"]
)


@router.post("/{factory_id}/calculate")
async def calculate_emissions(factory_id: str):

    try:
        emission_result = await calculate_factory_emissions(
            factory_id
        )

        recommendation_result = (
            await create_recommendations_for_factory(
                factory_id
            )
        )

        return {
            "emissions": emission_result,
            "recommendations": recommendation_result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )