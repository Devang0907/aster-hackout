from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from prisma.errors import PrismaError

from app.api.dependencies import FactoryOperator
from app.core.database import get_database
from app.schemas.recommendation import RecommendationStatusUpdate
from app.schemas.simulation import SimulationCreate
from app.services import operational
from app.services import recommendations as recommendation_service
from app.services import simulations as simulation_service
from app.services.errors import ServiceError

router = APIRouter(prefix="/factories/{factory_id}", tags=["insights"])
Database = Annotated[Any, Depends(get_database)]


@router.get("/carbon-results")
async def carbon_results(
    factory_id: UUID, current_user: FactoryOperator, database: Database
) -> list[Any]:
    return await operational.list_carbon_results(factory_id, current_user, database)


@router.get("/recommendations")
async def recommendations(
    factory_id: UUID, current_user: FactoryOperator, database: Database
) -> list[Any]:
    return await recommendation_service.list_recommendations(
        factory_id, current_user, database
    )


@router.patch("/recommendations/{recommendation_id}")
async def update_recommendation(
    factory_id: UUID,
    recommendation_id: UUID,
    payload: RecommendationStatusUpdate,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    return await recommendation_service.update_recommendation_status(
        factory_id,
        recommendation_id,
        payload.status,
        current_user,
        database,
    )


@router.get("/simulations")
async def simulations(
    factory_id: UUID, current_user: FactoryOperator, database: Database
) -> list[Any]:
    return await simulation_service.list_simulations(factory_id, current_user, database)


@router.post("/simulations", status_code=201)
async def create_simulation(
    factory_id: UUID,
    payload: SimulationCreate,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    try:
        return await simulation_service.create_simulation(
            factory_id, payload, current_user, database
        )
    except ServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc
    except PrismaError as exc:
        import logging
        logging.error(f"PrismaError creating simulation: {exc}")
        raise HTTPException(
            status_code=503,
            detail=f"Simulation could not be created: {str(exc)}",
        ) from exc


@router.get("/dashboard-summary")
async def dashboard_summary(
    factory_id: UUID, current_user: FactoryOperator, database: Database
) -> dict[str, Any]:
    """Get dashboard summary metrics for a factory."""
    await operational.assert_factory_operational_access(current_user, factory_id, database)

    carbon_results = await database.carbonresult.find_many(
        where={"factoryId": str(factory_id)},
        order={"calculatedAt": "desc"},
        take=1,
    )
    latest_result = carbon_results[0] if carbon_results else None
    net_co2e = float(latest_result.netCo2e) if latest_result else 0.0

    recommendations = []
    if latest_result:
        recommendations = await database.recommendation.find_many(
            where={"factoryId": str(factory_id), "resultId": latest_result.id}
        )
    active_recommendations = sum(
        str(getattr(item.status, "value", item.status)) != "rejected"
        for item in recommendations
    )

    leak_points = 0
    if latest_result:
        emission_sources = await database.emissionsource.find_many(
            where={"resultId": str(latest_result.id)},
        )
        leak_points = sum(float(item.emissionsCo2e) > 0 for item in emission_sources)

    simulations = await database.simulation.find_many(
        where={"factoryId": str(factory_id)},
    )

    return {
        # Kept for the existing client while making the net basis and unit explicit.
        "totalCo2e": net_co2e,
        "netCo2e": net_co2e,
        "emissionsUnit": "kgCO2e",
        "carbonIntensity": (
            float(latest_result.carbonIntensity)
            if latest_result and latest_result.carbonIntensity is not None
            else None
        ),
        "carbonIntensityUnit": (
            latest_result.carbonIntensityUnit if latest_result else None
        ),
        "activeRecommendations": active_recommendations,
        "leakPoints": leak_points,
        "simulationCount": len(simulations),
        "latestResultId": latest_result.id if latest_result else None,
    }
