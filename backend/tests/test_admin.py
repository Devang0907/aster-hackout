from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.schemas.user import UserContext, UserRole
from app.services.admin import set_user_active


class UserDelegate:
    async def find_unique(self, where):  # noqa: ANN001
        return SimpleNamespace(id=where["id"])


class AuditDelegate:
    def __init__(self) -> None:
        self.entries: list[dict[str, object]] = []

    async def create(self, data):  # noqa: ANN001
        self.entries.append(data)


class Transaction:
    def __init__(self, auditlog: AuditDelegate) -> None:
        self.user = UserDelegate()
        self.auditlog = auditlog

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False


class FakeDatabase:
    def __init__(self) -> None:
        self.user = UserDelegate()
        self.auditlog = AuditDelegate()

    def tx(self) -> Transaction:
        return Transaction(self.auditlog)


@pytest.mark.asyncio
async def test_admin_user_deactivation_is_audited() -> None:
    admin = UserContext(
        id=uuid4(),
        fullName="Admin",
        email="admin@example.com",
        role=UserRole.admin,
    )
    database = FakeDatabase()
    user_id = uuid4()

    await set_user_active(admin, user_id, False, database)

    assert database.auditlog.entries == [
        {
            "userId": str(admin.id),
            "action": "USER_DEACTIVATED",
            "entityType": "User",
            "entityId": str(user_id),
        }
    ]