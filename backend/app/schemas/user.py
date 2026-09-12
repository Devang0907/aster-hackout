from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import ApiModel


class UserRole(StrEnum):
    admin = "admin"
    factory_owner = "factory_owner"
    factory_manager = "factory_manager"


class UserCreate(ApiModel):
    id: UUID
    fullName: Annotated[str, Field(min_length=1, max_length=150)]
    email: EmailStr
    role: UserRole
    phone: Annotated[str, Field(max_length=20)] | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class ManagerAccountCreate(ApiModel):
    id: UUID | None = None
    fullName: Annotated[str, Field(min_length=1, max_length=150)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)] | None = None
    phone: Annotated[str, Field(max_length=20)] | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class UserContext(ApiModel):
    id: UUID
    fullName: str
    email: str
    role: UserRole
    isActive: bool = True
