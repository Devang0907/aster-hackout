from typing import Any
from uuid import UUID

from app.schemas.user import UserContext, UserRole
from app.services.errors import ForbiddenError, NotFoundError


async def get_accessible_factory_ids(user: UserContext, database: Any) -> list[UUID]:
    """Return operationally accessible factories; admins intentionally get none."""
    if user.role == UserRole.admin:
        return []
    field = "ownerId" if user.role == UserRole.factory_owner else "managerId"
    factories = await database.factory.find_many(
        where={field: str(user.id), "isActive": True},
        select={"id": True},
    )
    return [UUID(str(factory.id)) for factory in factories]


async def assert_factory_operational_access(
    user: UserContext,
    factory_id: UUID,
    database: Any,
) -> Any:
    if user.role == UserRole.admin:
        raise ForbiddenError("admins cannot access confidential factory operational data")
    principal_field = "ownerId" if user.role == UserRole.factory_owner else "managerId"
    factory = await database.factory.find_first(
        where={"id": str(factory_id), principal_field: str(user.id), "isActive": True}
    )
    if factory is None:
        # Do not reveal whether another tenant's factory exists.
        raise NotFoundError("factory not found")
    return factory


async def assert_factory_owner_access(
    user: UserContext,
    factory_id: UUID,
    database: Any,
) -> Any:
    if user.role != UserRole.factory_owner:
        raise ForbiddenError("factory owner role required")
    factory = await database.factory.find_first(
        where={"id": str(factory_id), "ownerId": str(user.id), "isActive": True}
    )
    if factory is None:
        raise NotFoundError("factory not found")
    return factory
