from typing import Any
from uuid import UUID

from app.schemas.user import UserContext, UserRole
from app.services.errors import ForbiddenError, NotFoundError

USER_BASIC_FIELDS = {
    "id": True,
    "fullName": True,
    "email": True,
    "role": True,
    "phone": True,
    "isActive": True,
    "createdAt": True,
    "updatedAt": True,
}

FACTORY_BASIC_FIELDS = {
    "id": True,
    "ownerId": True,
    "managerId": True,
    "name": True,
    "industryType": True,
    "city": True,
    "state": True,
    "country": True,
    "isActive": True,
    "createdAt": True,
    "updatedAt": True,
}


def _assert_admin(user: UserContext) -> None:
    if user.role != UserRole.admin:
        raise ForbiddenError("admin role required")


async def list_user_metadata(user: UserContext, database: Any) -> list[Any]:
    _assert_admin(user)
    return await database.user.find_many(select=USER_BASIC_FIELDS, order={"createdAt": "desc"})


async def list_factory_metadata(user: UserContext, database: Any) -> list[Any]:
    _assert_admin(user)
    return await database.factory.find_many(
        select=FACTORY_BASIC_FIELDS,
        order={"createdAt": "desc"},
    )


async def set_user_active(user: UserContext, user_id: UUID, active: bool, database: Any) -> Any:
    _assert_admin(user)
    found = await database.user.find_unique(where={"id": str(user_id)})
    if found is None:
        raise NotFoundError("user not found")
    async with database.tx() as transaction:
        result = await transaction.user.update(
            where={"id": str(user_id)}, data={"isActive": active}
        )
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "action": "USER_ACTIVATED" if active else "USER_DEACTIVATED",
                "entityType": "User",
                "entityId": str(user_id),
            }
        )
    return result


async def set_factory_active(
    user: UserContext, factory_id: UUID, active: bool, database: Any
) -> Any:
    _assert_admin(user)
    found = await database.factory.find_unique(where={"id": str(factory_id)})
    if found is None:
        raise NotFoundError("factory not found")
    async with database.tx() as transaction:
        result = await transaction.factory.update(
            where={"id": str(factory_id)}, data={"isActive": active}
        )
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": str(factory_id),
                "action": "FACTORY_ACTIVATED" if active else "FACTORY_DEACTIVATED",
                "entityType": "Factory",
                "entityId": str(factory_id),
            }
        )
    return result
