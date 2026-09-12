from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.repositories.helpers import to_prisma_data
from app.schemas.carbon import (
    CarbonCreditResultCreate,
    CarbonResultCreate,
    EmissionSourceCreate,
    MlPipelineRunCreate,
    PipelineRunStatus,
)
from app.schemas.recommendation import RecommendationCreate
from app.services.errors import ConflictError, NotFoundError


async def _period(factory_id: UUID, period_id: UUID, database: Any) -> Any:
    period = await database.reportingperiod.find_first(
        where={"id": str(period_id), "factoryId": str(factory_id)}
    )
    if period is None:
        raise NotFoundError("reporting period not found")
    return period


async def create_pipeline_run(
    factory_id: UUID, payload: MlPipelineRunCreate, database: Any
) -> Any:
    await _period(factory_id, payload.reportingPeriodId, database)
    data = to_prisma_data(payload.model_dump())
    data["factoryId"] = str(factory_id)
    return await database.mlpipelinerun.create(data=data)


async def update_pipeline_run(
    run_id: UUID,
    status: str,
    database: Any,
    error_message: str | None = None,
) -> Any:
    run = await database.mlpipelinerun.find_unique(where={"id": str(run_id)})
    if run is None:
        raise NotFoundError("pipeline run not found")
    if status not in {item.value for item in PipelineRunStatus}:
        raise ConflictError("invalid pipeline run status")
    current_status = str(getattr(run.status, "value", run.status))
    valid_transitions = {
        "queued": {"running", "failed"},
        "running": {"completed", "failed"},
        "completed": set(),
        "failed": set(),
    }
    if status != current_status and status not in valid_transitions[current_status]:
        raise ConflictError(f"pipeline run cannot move from {current_status} to {status}")
    now = datetime.now(UTC)
    data: dict[str, Any] = {"status": status}
    if status == "running":
        data["startedAt"] = now
    if status in {"completed", "failed"}:
        data["completedAt"] = now
    if error_message is not None:
        data["errorMessage"] = error_message
    return await database.mlpipelinerun.update(where={"id": str(run_id)}, data=data)


async def complete_pipeline_run(
    factory_id: UUID,
    run_id: UUID,
    result_payload: CarbonResultCreate,
    source_payloads: list[EmissionSourceCreate],
    recommendation_payloads: list[RecommendationCreate],
    database: Any,
) -> Any:
    run = await database.mlpipelinerun.find_first(
        where={"id": str(run_id), "factoryId": str(factory_id)}
    )
    if run is None:
        raise NotFoundError("pipeline run not found")
    current_status = str(getattr(run.status, "value", run.status))
    if current_status != "running":
        raise ConflictError("only running pipeline runs may be completed")
    period = await _period(factory_id, result_payload.reportingPeriodId, database)
    if str(run.reportingPeriodId) != str(period.id):
        raise ConflictError("pipeline run and carbon result must use the same reporting period")

    result_payload = result_payload.model_copy(update={"pipelineRunId": run_id})
    async with database.tx() as transaction:
        result = await transaction.carbonresult.create(
            data=to_prisma_data(result_payload.model_dump(exclude_none=True))
            | {"factoryId": str(factory_id)}
        )
        for payload in source_payloads:
            source_data = to_prisma_data(payload.model_dump(exclude_none=True))
            source_data["resultId"] = result.id
            await transaction.emissionsource.create(data=source_data)
        for payload in recommendation_payloads:
            recommendation_data = to_prisma_data(payload.model_dump(exclude_none=True))
            recommendation_data["factoryId"] = str(factory_id)
            recommendation_data["resultId"] = result.id
            await transaction.recommendation.create(data=recommendation_data)
        completed_at = datetime.now(UTC)
        await transaction.mlpipelinerun.update(
            where={"id": str(run_id)},
            data={"status": "completed", "completedAt": completed_at},
        )
        await transaction.reportingperiod.update(
            where={"id": str(period.id)},
            data={"status": "completed"},
        )
    return result


async def create_carbon_result(
    factory_id: UUID, payload: CarbonResultCreate, database: Any
) -> Any:
    period = await _period(factory_id, payload.reportingPeriodId, database)
    if payload.pipelineRunId is not None:
        run = await database.mlpipelinerun.find_first(
            where={
                "id": str(payload.pipelineRunId),
                "factoryId": str(factory_id),
                "reportingPeriodId": str(period.id),
            }
        )
        if run is None:
            raise NotFoundError("pipeline run not found")
    data = to_prisma_data(payload.model_dump(exclude_none=True))
    data["factoryId"] = str(factory_id)
    return await database.carbonresult.create(data=data)


async def create_emission_sources(
    factory_id: UUID, result_id: UUID, payloads: list[EmissionSourceCreate], database: Any
) -> list[Any]:
    result = await database.carbonresult.find_first(
        where={"id": str(result_id), "factoryId": str(factory_id)}
    )
    if result is None:
        raise NotFoundError("carbon result not found")
    created = []
    async with database.tx() as transaction:
        for payload in payloads:
            data = to_prisma_data(payload.model_dump())
            data["resultId"] = str(result_id)
            created.append(await transaction.emissionsource.create(data=data))
    return created


async def create_recommendations(
    factory_id: UUID, payloads: list[RecommendationCreate], database: Any
) -> list[Any]:
    created = []
    async with database.tx() as transaction:
        for payload in payloads:
            result = await transaction.carbonresult.find_first(
                where={"id": str(payload.resultId), "factoryId": str(factory_id)}
            )
            if result is None:
                raise NotFoundError("carbon result not found")
            data = to_prisma_data(payload.model_dump(exclude_none=True))
            data["factoryId"] = str(factory_id)
            created.append(await transaction.recommendation.create(data=data))
    return created


async def create_carbon_credit_result(
    factory_id: UUID, payload: CarbonCreditResultCreate, database: Any
) -> Any:
    await _period(factory_id, payload.reportingPeriodId, database)
    data = to_prisma_data(payload.model_dump(exclude_none=True))
    data["factoryId"] = str(factory_id)
    return await database.carboncreditresult.create(data=data)