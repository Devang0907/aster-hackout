from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel

from app.repositories.helpers import to_prisma_data
from app.schemas.user import UserContext
from app.services.authorization import assert_factory_operational_access
from app.services.errors import ConflictError, ImmutableHistoryError, NotFoundError

OperationalKind = Literal["material", "energy", "waste", "logistics"]

DELEGATES: dict[OperationalKind, tuple[str, str]] = {
    "material": ("factorymaterialusage", "MATERIAL_USAGE_UPDATED"),
    "energy": ("energyusage", "ENERGY_DATA_UPDATED"),
    "waste": ("wastestream", "WASTE_DATA_UPDATED"),
    "logistics": ("logistics", "LOGISTICS_DATA_UPDATED"),
}


async def _get_period(factory_id: UUID, period_id: UUID, database: Any) -> Any:
    period = await database.reportingperiod.find_first(
        where={"id": str(period_id), "factoryId": str(factory_id)}
    )
    if period is None:
        raise NotFoundError("reporting period not found")
    return period


async def _assert_period_editable(factory_id: UUID, period_id: UUID, database: Any) -> None:
    period = await _get_period(factory_id, period_id, database)
    status = str(getattr(period.status, "value", period.status))
    if status != "draft":
        raise ConflictError("operational data can only be changed while the period is draft")


async def create_operational_record(
    kind: OperationalKind,
    factory_id: UUID,
    payload: BaseModel,
    user: UserContext,
    database: Any,
) -> Any:
    await assert_factory_operational_access(user, factory_id, database)
    period_id = payload.reportingPeriodId
    await _assert_period_editable(factory_id, period_id, database)
    if kind == "material":
        material = await database.material.find_first(
            where={"id": str(payload.materialId), "isActive": True}
        )
        if material is None:
            raise NotFoundError("material not found")
    delegate_name, action = DELEGATES[kind]
    data = to_prisma_data(payload.model_dump(exclude_none=True))
    data["factoryId"] = str(factory_id)
    async with database.tx() as transaction:
        result = await getattr(transaction, delegate_name).create(data=data)
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": str(factory_id),
                "action": action,
                "entityType": type(result).__name__,
                "entityId": result.id,
            }
        )
    return result


async def list_operational_records(
    kind: OperationalKind,
    factory_id: UUID,
    user: UserContext,
    database: Any,
    reporting_period_id: UUID | None = None,
) -> list[Any]:
    await assert_factory_operational_access(user, factory_id, database)
    if reporting_period_id is not None:
        await _get_period(factory_id, reporting_period_id, database)
    delegate_name, _ = DELEGATES[kind]
    where: dict[str, Any] = {"factoryId": str(factory_id)}
    if reporting_period_id:
        where["reportingPeriodId"] = str(reporting_period_id)
    return await getattr(database, delegate_name).find_many(
        where=where, order={"createdAt": "desc"}
    )


async def list_carbon_results(factory_id: UUID, user: UserContext, database: Any) -> list[Any]:
    await assert_factory_operational_access(user, factory_id, database)
    return await database.carbonresult.find_many(
        where={"factoryId": str(factory_id)},
        include={"emissionSources": True},
        order={"calculatedAt": "desc"},
    )


async def delete_historical_result(*_: Any, **__: Any) -> None:
    raise ImmutableHistoryError("historical carbon results cannot be deleted")
