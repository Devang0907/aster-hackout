from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.carbon import ReportingPeriodCreate
from app.schemas.user import UserContext, UserRole
from app.services.errors import ConflictError
from app.services.reporting import create_reporting_period


class FactoryDelegate:
    async def find_first(self, where):  # noqa: ANN001
        return SimpleNamespace(id=where["id"])


class ReportingPeriodDelegate:
    async def find_first(self, where):  # noqa: ANN001
        return SimpleNamespace(id=uuid4())


class FakeDatabase:
    def __init__(self) -> None:
        self.factory = FactoryDelegate()
        self.reportingperiod = ReportingPeriodDelegate()


@pytest.mark.asyncio
async def test_duplicate_reporting_period_is_rejected() -> None:
    owner = UserContext(
        id=uuid4(),
        fullName="Factory Owner",
        email="owner@example.com",
        role=UserRole.factory_owner,
    )
    payload = ReportingPeriodCreate(
        periodStart=date(2026, 1, 1), periodEnd=date(2026, 1, 31)
    )

    with pytest.raises(ConflictError, match="already exists"):
        await create_reporting_period(owner.id, payload, owner, FakeDatabase())