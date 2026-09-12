from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.core.database import get_database
from app.schemas.user import UserContext, UserRole
from app.services.errors import ForbiddenError

bearer = HTTPBearer(auto_error=False)
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
DevelopmentUserId = Annotated[str | None, Header(alias="X-User-Id")]
SettingsDependency = Annotated[Settings, Depends(get_settings)]
DatabaseDependency = Annotated[Any, Depends(get_database)]


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _to_context(user: Any) -> UserContext:
    if not user or not user.isActive:
        raise ForbiddenError("user is inactive or does not exist")
    return UserContext(
        id=UUID(str(user.id)),
        fullName=user.fullName,
        email=user.email,
        role=UserRole(_enum_value(user.role)),
        isActive=user.isActive,
    )


async def get_current_user(
    credentials: Credentials,
    settings: SettingsDependency,
    database: DatabaseDependency,
    x_user_id: DevelopmentUserId = None,
) -> UserContext:
    if settings.auth_mode == "development_header":
        if not x_user_id:
            raise ForbiddenError("X-User-Id is required in development_header mode")
        try:
            subject = UUID(x_user_id)
        except ValueError as exc:
            raise ForbiddenError("X-User-Id must be a UUID") from exc
    else:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise ForbiddenError("Bearer authentication is required")
        if settings.jwt_secret is None:
            raise ForbiddenError("JWT authentication is not configured")
        options: dict[str, Any] = {"require": ["sub", "exp"]}
        decode_kwargs: dict[str, Any] = {
            "key": settings.jwt_secret.get_secret_value(),
            "algorithms": [settings.jwt_algorithm],
            "options": options,
        }
        if settings.jwt_audience:
            decode_kwargs["audience"] = settings.jwt_audience
        else:
            options["verify_aud"] = False
        if settings.jwt_issuer:
            decode_kwargs["issuer"] = settings.jwt_issuer
        try:
            payload = jwt.decode(credentials.credentials, **decode_kwargs)
            subject = UUID(str(payload["sub"]))
        except (jwt.PyJWTError, ValueError, KeyError) as exc:
            raise ForbiddenError("invalid authentication token") from exc

    user = await database.user.find_unique(where={"id": str(subject)})
    return _to_context(user)
