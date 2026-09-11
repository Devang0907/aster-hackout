from typing import Any
from uuid import UUID

from app.repositories.helpers import to_prisma_data
from app.schemas.factory import FactoryCreate, FactoryUpdate
from app.schemas.user import ManagerAccountCreate, UserContext, UserRole
from app.services.authorization import (
    assert_factory_operational_access,
    assert_factory_owner_access,
)
from app.services.errors import ConflictError, ForbiddenError


async def list_accessible_factories(user: UserContext, database: Any) -> list[Any]:
    if user.role == UserRole.admin:
        raise ForbiddenError("admins must use the metadata-only endpoint")
    field = "ownerId" if user.role == UserRole.factory_owner else "managerId"
    return await database.factory.find_many(
        where={field: str(user.id), "isActive": True},
        order={"createdAt": "desc"},
    )


async def create_factory(user: UserContext, payload: FactoryCreate, database: Any) -> Any:
    if user.role != UserRole.factory_owner:
        raise ForbiddenError("only factory owners can register factories")
    data = to_prisma_data(payload.model_dump(exclude_none=True))
    data["ownerId"] = str(user.id)
    async with database.tx() as transaction:
        factory = await transaction.factory.create(data=data)
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": factory.id,
                "action": "FACTORY_CREATED",
                "entityType": "Factory",
                "entityId": factory.id,
            }
        )
    return factory


async def update_factory(
    user: UserContext,
    factory_id: UUID,
    payload: FactoryUpdate,
    database: Any,
) -> Any:
    await assert_factory_owner_access(user, factory_id, database)
    return await database.factory.update(
        where={"id": str(factory_id)},
        data=to_prisma_data(payload.model_dump(exclude_none=True)),
    )


async def create_and_assign_manager(
    owner: UserContext,
    factory_id: UUID,
    payload: ManagerAccountCreate,
    database: Any,
) -> Any:
    await assert_factory_owner_access(owner, factory_id, database)
    manager_id = str(payload.id)
    existing_assignment = await database.factory.find_first(where={"managerId": manager_id})
    if existing_assignment is not None and str(existing_assignment.id) != str(factory_id):
        raise ConflictError("manager is already assigned to another factory")

    existing_by_id = await database.user.find_unique(where={"id": manager_id})
    existing_by_email = await database.user.find_unique(where={"email": str(payload.email).lower()})
    if existing_by_email is not None and str(existing_by_email.id) != manager_id:
        raise ConflictError("email is already assigned to another account")
    existing_role = (
        str(getattr(existing_by_id.role, "value", existing_by_id.role))
        if existing_by_id is not None
        else None
    )
    if existing_role is not None and existing_role != UserRole.factory_manager.value:
        raise ConflictError("the supplied user ID belongs to a non-manager account")

    manager_data = to_prisma_data(payload.model_dump(exclude_none=True))
    manager_data["email"] = str(payload.email).lower()
    manager_data["role"] = UserRole.factory_manager.value
    async with database.tx() as transaction:
        if existing_by_id is None:
            await transaction.user.create(data=manager_data)
        manager_factory = await transaction.factory.update(
            where={"id": str(factory_id)}, data={"managerId": manager_id}
        )
        await transaction.auditlog.create(
            data={
                "userId": str(owner.id),
                "factoryId": str(factory_id),
                "action": "MANAGER_ASSIGNED",
                "entityType": "Factory",
                "entityId": str(factory_id),
                "metadata": {"managerId": manager_id},
            }
        )
    return manager_factory


async def ensure_operational_access(user: UserContext, factory_id: UUID, database: Any) -> Any:
    return await assert_factory_operational_access(user, factory_id, database)
