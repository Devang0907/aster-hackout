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
    data = to_prisma_data(payload.model_dump(exclude_none=True))
    data.update({"factoryId": str(factory_id), "createdById": str(user.id)})
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
