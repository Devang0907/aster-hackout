from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import FactoryOperator
from app.core.database import get_database
from app.schemas.recommendation import RecommendationStatusUpdate
from app.schemas.simulation import SimulationCreate
from app.services import operational
from app.services import recommendations as recommendation_service
from app.services import simulations as simulation_service

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
    return await simulation_service.create_simulation(
        factory_id, payload, current_user, database
    )


@router.get("/dashboard-summary")
async def dashboard_summary(
    factory_id: UUID, current_user: FactoryOperator, database: Database
) -> dict[str, Any]:
    """Get dashboard summary metrics for a factory."""
    await operational.assert_factory_operational_access(current_user, factory_id, database)
    
    # Get latest carbon result for total CO2e
    carbon_results = await database.carbonresult.find_many(
        where={"factoryId": str(factory_id)},
        order={"calculatedAt": "desc"},
        take=1,
    )
    latest_result = carbon_results[0] if carbon_results else None
    total_co2e = float(latest_result.netCo2e) if latest_result else 0.0
    
    # Count active recommendations (not rejected)
    recommendations = await database.recommendation.find_many(
        where={
            "factoryId": str(factory_id),
            "status": {"not": {"equals": "rejected"}},
        },
    )
    active_recommendations = len(recommendations)
    
    # Count leak points from latest result
    leak_points = 0
    if latest_result:
        emission_sources = await database.emissionsource.find_many(
            where={"carbonResultId": str(latest_result.id)},
        )
        leak_points = len(emission_sources)
    
    # Count simulations
    simulations = await database.simulation.find_many(
        where={"factoryId": str(factory_id)},
    )
    simulation_count = len(simulations)
    
    return {
        "totalCo2e": total_co2e,
        "activeRecommendations": active_recommendations,
        "leakPoints": leak_points,
        "simulationCount": simulation_count,
    }
