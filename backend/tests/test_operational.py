from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.material import MaterialUsageCreate
from app.schemas.user import UserContext, UserRole
from app.services.errors import NotFoundError
from app.services.operational import create_operational_record


class FactoryDelegate:
    async def find_first(self, where):  # noqa: ANN001
        return SimpleNamespace(id=where["id"])


class PeriodDelegate:
    async def find_first(self, where):  # noqa: ANN001
        return SimpleNamespace(status="draft")


class MaterialDelegate:
    async def find_first(self, where):  # noqa: ANN001
        return None


class FakeDatabase:
    def __init__(self) -> None:
        self.factory = FactoryDelegate()
        self.reportingperiod = PeriodDelegate()
        self.material = MaterialDelegate()


@pytest.mark.asyncio
async def test_unknown_material_is_rejected_before_creation() -> None:
    user = UserContext(
        id=uuid4(),
        fullName="Factory Owner",
        email="owner@example.com",
        role=UserRole.factory_owner,
    )
    payload = MaterialUsageCreate(
        reportingPeriodId=uuid4(), materialId=uuid4(), quantity=10, unit="kg"
    )

    with pytest.raises(NotFoundError, match="material not found"):
        await create_operational_record("material", uuid4(), payload, user, FakeDatabase())