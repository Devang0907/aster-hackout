from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.repositories.helpers import to_prisma_data
from app.schemas.carbon import ReportingPeriodCreate
from app.schemas.user import UserContext
from app.services.authorization import assert_factory_operational_access
from app.services.errors import ConflictError, NotFoundError


async def create_reporting_period(
    factory_id: UUID,
    payload: ReportingPeriodCreate,
    user: UserContext,
    database: Any,
) -> Any:
    await assert_factory_operational_access(user, factory_id, database)
    data = to_prisma_data(payload.model_dump())
    data["factoryId"] = str(factory_id)
    return await database.reportingperiod.create(data=data)


async def list_reporting_periods(
    factory_id: UUID, user: UserContext, database: Any
) -> list[Any]:
    await assert_factory_operational_access(user, factory_id, database)
    return await database.reportingperiod.find_many(
        where={"factoryId": str(factory_id)}, order={"periodStart": "desc"}
    )


async def submit_reporting_period(
    factory_id: UUID,
    period_id: UUID,
    user: UserContext,
    database: Any,
) -> Any:
    await assert_factory_operational_access(user, factory_id, database)
    period = await database.reportingperiod.find_first(
        where={"id": str(period_id), "factoryId": str(factory_id)}
    )
    if period is None:
        raise NotFoundError("reporting period not found")
    status = str(getattr(period.status, "value", period.status))
    if status != "draft":
        raise ConflictError("only draft reporting periods may be submitted")
    submitted_at = datetime.now(UTC)
    async with database.tx() as transaction:
        result = await transaction.reportingperiod.update(
            where={"id": str(period_id)},
            data={
                "status": "submitted",
                "submittedById": str(user.id),
                "submittedAt": submitted_at,
            },
        )
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": str(factory_id),
                "action": "REPORT_SUBMITTED",
                "entityType": "ReportingPeriod",
                "entityId": str(period_id),
            }
        )
    return result
