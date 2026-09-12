from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import AdminUser
from app.core.database import get_database
from app.services import admin as service

router = APIRouter(prefix="/admin", tags=["admin"])
Database = Annotated[Any, Depends(get_database)]


@router.get("/users")
async def users(current_user: AdminUser, database: Database) -> list[Any]:
    return await service.list_user_metadata(current_user, database)


@router.get("/factories")
async def factories(current_user: AdminUser, database: Database) -> list[Any]:
    return await service.list_factory_metadata(current_user, database)


@router.patch("/users/{user_id}/active")
async def set_user_active(
    user_id: UUID,
    current_user: AdminUser,
    database: Database,
    active: bool = Query(...),
) -> Any:
    return await service.set_user_active(current_user, user_id, active, database)


@router.patch("/factories/{factory_id}/active")
async def set_factory_active(
    factory_id: UUID,
    current_user: AdminUser,
    database: Database,
    active: bool = Query(...),
) -> Any:
    return await service.set_factory_active(current_user, factory_id, active, database)
