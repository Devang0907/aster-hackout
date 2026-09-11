from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.carbon import CarbonResultCreate, MlPipelineRunCreate
from app.services.calculations import create_carbon_result, create_pipeline_run
from app.services.errors import NotFoundError


class PeriodDelegate:
    def __init__(self, period) -> None:
        self.period = period

    async def find_first(self, where):  # noqa: ANN001
        if where["id"] == self.period.id and where["factoryId"] == self.period.factoryId:
            return self.period
        return None


class PipelineDelegate:
    async def find_first(self, where):  # noqa: ANN001
        return None


class FakeDatabase:
    def __init__(self, period) -> None:
        self.reportingperiod = PeriodDelegate(period)
        self.mlpipelinerun = PipelineDelegate()


@pytest.mark.asyncio
async def test_pipeline_run_requires_factory_period() -> None:
    factory_id = uuid4()
    period_id = uuid4()
    period = SimpleNamespace(id=str(period_id), factoryId=str(uuid4()))
    payload = MlPipelineRunCreate(
        reportingPeriodId=period_id,
        pipelineVersion="calc-v1",
    )

    with pytest.raises(NotFoundError, match="reporting period"):
        await create_pipeline_run(factory_id, payload, FakeDatabase(period))


@pytest.mark.asyncio
async def test_carbon_result_requires_pipeline_run_from_same_factory() -> None:
    factory_id = uuid4()
    period_id = uuid4()
    run_id = uuid4()
    period = SimpleNamespace(id=str(period_id), factoryId=str(factory_id))
    payload = CarbonResultCreate(
        reportingPeriodId=period_id,
        pipelineRunId=run_id,
        totalCo2e=100,
        netCo2e=100,
        calculationVersion="calc-v1",
    )

    with pytest.raises(NotFoundError, match="pipeline run"):
        await create_carbon_result(factory_id, payload, FakeDatabase(period))