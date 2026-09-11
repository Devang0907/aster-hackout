from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.factory import ManagerAssignment
from app.schemas.user import UserContext, UserRole
from app.services.errors import ConflictError
from app.services.factories import create_and_assign_manager


class FactoryDelegate:
    async def find_first(self, where):  # noqa: ANN001
        if "ownerId" in where:
            return SimpleNamespace(id=where["id"])
        return None


class UserDelegate:
    def __init__(self, manager):
        self.manager = manager

    async def find_unique(self, where):  # noqa: ANN001
        if where.get("id") == self.manager.id:
            return self.manager
        return None


class FakeDatabase:
    def __init__(self, manager):
        self.factory = FactoryDelegate()
        self.user = UserDelegate(manager)


@pytest.mark.asyncio
async def test_inactive_manager_cannot_be_assigned() -> None:
    owner_id = uuid4()
    factory_id = uuid4()
    manager_id = uuid4()
    manager = SimpleNamespace(
        id=str(manager_id), role=UserRole.factory_manager, isActive=False
    )
    owner = UserContext(
        id=owner_id,
        fullName="Factory Owner",
        email="owner@example.com",
        role=UserRole.factory_owner,
    )
    payload = ManagerAssignment(
        manager={
            "id": manager_id,
            "fullName": "Inactive Manager",
            "email": "manager@example.com",
        }
    )

    with pytest.raises(ConflictError, match="inactive"):
        await create_and_assign_manager(owner, factory_id, payload.manager, FakeDatabase(manager))