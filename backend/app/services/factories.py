from typing import Any
from uuid import UUID

from app.repositories.helpers import to_prisma_data
from app.schemas.factory import FactoryCreate, FactoryUpdate
from app.schemas.user import ManagerAccountCreate, UserContext, UserRole
from app.security.passwords import hash_password
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
    async with database.tx() as transaction:
        factory = await transaction.factory.update(
            where={"id": str(factory_id)},
            data=to_prisma_data(payload.model_dump(exclude_none=True)),
        )
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": str(factory_id),
                "action": "FACTORY_UPDATED",
                "entityType": "Factory",
                "entityId": str(factory_id),
            }
        )
    return factory


async def create_and_assign_manager(
    owner: UserContext,
    factory_id: UUID,
    payload: ManagerAccountCreate,
    database: Any,
) -> Any:
    await assert_factory_owner_access(owner, factory_id, database)
    if payload.id is not None:
        manager_id = str(payload.id)
        existing_assignment = await database.factory.find_first(where={"managerId": manager_id})
        if existing_assignment is not None and str(existing_assignment.id) != str(factory_id):
            raise ConflictError("manager is already assigned to another factory")
        existing_by_id = await database.user.find_unique(where={"id": manager_id})
        if existing_by_id is None or existing_by_id.role != UserRole.factory_manager:
            raise ConflictError("the supplied user ID is not a factory manager")
        if not existing_by_id.isActive:
            raise ConflictError("the supplied manager account is inactive")
    else:
        existing_by_id = None
        if payload.password is None:
            raise ConflictError("a password is required for a new manager account")
        existing_by_email = await database.user.find_unique(
            where={"email": str(payload.email).lower()}
        )
        if existing_by_email is not None:
            raise ConflictError("email is already assigned to another account")
        import uuid
        manager_id = str(uuid.uuid4())
    factory = await database.factory.find_first(where={"id": str(factory_id)})
    if factory is not None and factory.managerId is not None:
        raise ConflictError("this factory already has a manager")

    manager_data = to_prisma_data(payload.model_dump(exclude_none=True))
    manager_data.pop("password", None)
    manager_data.pop("id", None)
    manager_data["id"] = manager_id
    if payload.password is not None:
        manager_data["passwordHash"] = hash_password(payload.password)
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
