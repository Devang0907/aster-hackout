import json
from typing import Any
from uuid import UUID

from app.repositories.helpers import to_prisma_data
from app.schemas.simulation import SimulationCreate
from app.schemas.user import UserContext
from app.services.authorization import assert_factory_operational_access
from app.services.errors import NotFoundError


async def create_simulation(
    factory_id: UUID,
    payload: SimulationCreate,
    user: UserContext,
    database: Any,
) -> Any:
    await assert_factory_operational_access(user, factory_id, database)
    base_result = await database.carbonresult.find_first(
        where={"id": str(payload.baseResultId), "factoryId": str(factory_id)}
    )
    if base_result is None:
        raise NotFoundError("base carbon result not found")
    # Manually construct data with correct field names for Prisma
    data = {
        "baseResultId": str(payload.baseResultId),
        "name": payload.name,
        "assumptions": json.dumps(payload.assumptions),
        "baselineCo2e": payload.baselineCo2e,
        "resultingCo2e": payload.resultingCo2e,
        "co2Reduction": payload.co2Reduction,
        "co2ReductionPercentage": payload.co2ReductionPercentage,
        "factoryId": str(factory_id),
        "createdById": str(user.id),
    }
    if payload.estimatedCost is not None:
        data["estimatedCost"] = payload.estimatedCost
    if payload.estimatedSavings is not None:
        data["estimatedSavings"] = payload.estimatedSavings
    if payload.paybackMonths is not None:
        data["paybackMonths"] = payload.paybackMonths
    async with database.tx() as transaction:
        simulation = await transaction.simulation.create(data=data)
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": str(factory_id),
                "action": "SIMULATION_CREATED",
                "entityType": "Simulation",
                "entityId": simulation.id,
            }
        )
    return simulation


async def list_simulations(
    factory_id: UUID, user: UserContext, database: Any
) -> list[Any]:
    await assert_factory_operational_access(user, factory_id, database)
    return await database.simulation.find_many(
        where={"factoryId": str(factory_id)}, order={"createdAt": "desc"}
    )
