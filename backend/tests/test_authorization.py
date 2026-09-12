from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.schemas.user import UserContext, UserRole
from app.services.authorization import (
    assert_factory_operational_access,
    get_accessible_factory_ids,
)
from app.services.errors import ForbiddenError, NotFoundError


class FactoryDelegate:
    def __init__(self, factories: list[SimpleNamespace]) -> None:
        self.factories = factories

    async def find_many(self, where, select=None):  # noqa: ANN001, ARG002
        return [factory for factory in self.factories if self._matches(factory, where)]

    async def find_first(self, where):  # noqa: ANN001
        return next(
            (factory for factory in self.factories if self._matches(factory, where)), None
        )

    @staticmethod
    def _matches(factory: SimpleNamespace, where: dict[str, object]) -> bool:
        return all(getattr(factory, key) == value for key, value in where.items())


class FakeDatabase:
    def __init__(self, factories: list[SimpleNamespace]) -> None:
        self.factory = FactoryDelegate(factories)


def user(role: UserRole, user_id: UUID) -> UserContext:
    return UserContext(
        id=user_id,
        fullName="Test User",
        email="test@example.com",
        role=role,
        isActive=True,
    )


@pytest.mark.asyncio
async def test_factory_owner_can_own_multiple_factories() -> None:
    owner_id = uuid4()
    factories = [
        SimpleNamespace(
            id=str(uuid4()), ownerId=str(owner_id), managerId=None, isActive=True
        ),
        SimpleNamespace(
            id=str(uuid4()), ownerId=str(owner_id), managerId=None, isActive=True
        ),
    ]
    accessible = await get_accessible_factory_ids(
        user(UserRole.factory_owner, owner_id), FakeDatabase(factories)
    )
    assert len(accessible) == 2


@pytest.mark.asyncio
async def test_factory_owner_authorization_restricts_to_owned_factories() -> None:
    owner_id = uuid4()
    owned_id = uuid4()
    other_id = uuid4()
    database = FakeDatabase(
        [
            SimpleNamespace(
                id=str(owned_id), ownerId=str(owner_id), managerId=None, isActive=True
            ),
            SimpleNamespace(
                id=str(other_id), ownerId=str(uuid4()), managerId=None, isActive=True
            ),
        ]
    )
    principal = user(UserRole.factory_owner, owner_id)
    assert await assert_factory_operational_access(principal, owned_id, database)
    with pytest.raises(NotFoundError):
        await assert_factory_operational_access(principal, other_id, database)


@pytest.mark.asyncio
async def test_factory_manager_authorization_restricts_to_single_factory() -> None:
    manager_id = uuid4()
    managed_id = uuid4()
    other_id = uuid4()
    database = FakeDatabase(
        [
            SimpleNamespace(
                id=str(managed_id), ownerId=str(uuid4()), managerId=str(manager_id), isActive=True
            ),
            SimpleNamespace(
                id=str(other_id), ownerId=str(uuid4()), managerId=str(uuid4()), isActive=True
            ),
        ]
    )
    principal = user(UserRole.factory_manager, manager_id)
    accessible = await get_accessible_factory_ids(principal, database)
    assert accessible == [managed_id]
    with pytest.raises(NotFoundError):
        await assert_factory_operational_access(principal, other_id, database)


@pytest.mark.asyncio
async def test_admin_cannot_access_confidential_operational_data() -> None:
    admin = user(UserRole.admin, uuid4())
    database = FakeDatabase([])
    assert await get_accessible_factory_ids(admin, database) == []
    with pytest.raises(ForbiddenError, match="confidential"):
        await assert_factory_operational_access(admin, uuid4(), database)
