from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from prisma.errors import UniqueViolationError

from app.repositories.helpers import to_prisma_data
from app.schemas.carbon import ReportingPeriodCreate
from app.schemas.user import UserContext
from app.services.authorization import assert_factory_operational_access
from app.services.errors import ConflictError, NotFoundError
from app.services.pipeline import run_reporting_period_pipeline


async def create_reporting_period(
    factory_id: UUID,
    payload: ReportingPeriodCreate,
    user: UserContext,
    database: Any,
) -> Any:
    await assert_factory_operational_access(user, factory_id, database)
    data = to_prisma_data(payload.model_dump())
    data["factoryId"] = str(factory_id)
    existing = await database.reportingperiod.find_first(
        where={
            "factoryId": str(factory_id),
            "periodStart": data["periodStart"],
            "periodEnd": data["periodEnd"],
        }
    )
    if existing is not None:
        existing_status_value = getattr(existing, "status", None)
        existing_status = str(
            getattr(existing_status_value, "value", existing_status_value)
        )
        if existing_status == "draft":
            return existing
        raise ConflictError("reporting period already exists and has been submitted")
    try:
        async with database.tx() as transaction:
            period = await transaction.reportingperiod.create(data=data)
            await transaction.auditlog.create(
                data={
                    "userId": str(user.id),
                    "factoryId": str(factory_id),
                    "action": "REPORTING_PERIOD_CREATED",
                    "entityType": "ReportingPeriod",
                    "entityId": period.id,
                }
            )
    except UniqueViolationError:
        # Another request may have created this period between the lookup and
        # insert. Reuse a still-editable draft instead of leaking a 500.
        period = await database.reportingperiod.find_first(
            where={
                "factoryId": str(factory_id),
                "periodStart": data["periodStart"],
                "periodEnd": data["periodEnd"],
            }
        )
        if period is None:
            raise
        period_status = str(getattr(period.status, "value", period.status))
        if period_status != "draft":
            raise ConflictError("reporting period already exists and has been submitted") from None
    return period


async def list_reporting_periods(
    factory_id: UUID, user: UserContext, database: Any
) -> list[Any]:
    await assert_factory_operational_access(user, factory_id, database)
    return await database.reportingperiod.find_many(
        where={"factoryId": str(factory_id)}, order={"periodStart": "desc"}
    )


async def delete_reporting_period(
    factory_id: UUID,
    period_id: UUID,
    user: UserContext,
    database: Any,
) -> None:
    await assert_factory_operational_access(user, factory_id, database)
    period = await database.reportingperiod.find_first(
        where={"id": str(period_id), "factoryId": str(factory_id)}
    )
    if period is None:
        raise NotFoundError("reporting period not found")
    async with database.tx() as transaction:
        await transaction.reportingperiod.delete(where={"id": str(period_id)})
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": str(factory_id),
                "action": "REPORTING_PERIOD_DELETED",
                "entityType": "ReportingPeriod",
                "entityId": str(period_id),
            }
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
        await transaction.reportingperiod.update(
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

    # Submission commits first (above), then the calculation/recommendation pipeline
    # runs against the now-submitted period. The pipeline itself moves the period
    # through processing -> completed (or -> failed on error) and creates the
    # CarbonResult, EmissionSource, and Recommendation rows.
    carbon_result = await run_reporting_period_pipeline(factory_id, period_id, database)
    period = await database.reportingperiod.find_first(where={"id": str(period_id)})
    return {"period": period, "carbonResult": carbon_result}
