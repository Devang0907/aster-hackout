from typing import Annotated

from fastapi import Depends

from app.schemas.user import UserContext, UserRole
from app.security.authentication import get_current_user
from app.services.errors import ForbiddenError

CurrentUser = Annotated[UserContext, Depends(get_current_user)]


async def require_admin(current_user: CurrentUser) -> UserContext:
    if current_user.role != UserRole.admin:
        raise ForbiddenError("admin role required")
    return current_user


async def require_factory_owner(current_user: CurrentUser) -> UserContext:
    if current_user.role != UserRole.factory_owner:
        raise ForbiddenError("factory owner role required")
    return current_user


async def require_factory_manager(current_user: CurrentUser) -> UserContext:
    if current_user.role != UserRole.factory_manager:
        raise ForbiddenError("factory manager role required")
    return current_user


async def require_factory_operator(current_user: CurrentUser) -> UserContext:
    if current_user.role not in {UserRole.factory_owner, UserRole.factory_manager}:
        raise ForbiddenError("factory operational access is restricted to owners and managers")
    return current_user


AdminUser = Annotated[UserContext, Depends(require_admin)]
OwnerUser = Annotated[UserContext, Depends(require_factory_owner)]
ManagerUser = Annotated[UserContext, Depends(require_factory_manager)]
FactoryOperator = Annotated[UserContext, Depends(require_factory_operator)]
