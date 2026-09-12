from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import FactoryOperator, OwnerUser
from app.core.database import get_database
from app.schemas.factory import FactoryCreate, FactoryUpdate, ManagerAssignment
from app.services import factories as service

router = APIRouter(prefix="/factories", tags=["factories"])
Database = Annotated[Any, Depends(get_database)]


@router.get("")
async def list_factories(current_user: FactoryOperator, database: Database) -> list[Any]:
    return await service.list_accessible_factories(current_user, database)


@router.post("", status_code=201)
async def register_factory(
    payload: FactoryCreate, current_user: OwnerUser, database: Database
) -> Any:
    return await service.create_factory(current_user, payload, database)


@router.patch("/{factory_id}")
async def update_factory(
    factory_id: UUID,
    payload: FactoryUpdate,
    current_user: OwnerUser,
    database: Database,
) -> Any:
    return await service.update_factory(current_user, factory_id, payload, database)


@router.post("/{factory_id}/manager", status_code=201)
async def assign_manager(
    factory_id: UUID,
    payload: ManagerAssignment,
    current_user: OwnerUser,
    database: Database,
) -> Any:
    return await service.create_and_assign_manager(
        current_user, factory_id, payload.manager, database
    )
