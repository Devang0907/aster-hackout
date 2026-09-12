from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.schemas.common import ApiModel, NonNegativeDecimal
from app.schemas.user import ManagerAccountCreate


class FactoryCreate(ApiModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    industryType: Annotated[str, Field(min_length=1, max_length=100)]
    description: str | None = None
    address: str | None = None
    city: Annotated[str, Field(min_length=1, max_length=100)]
    state: Annotated[str, Field(min_length=1, max_length=100)]
    country: Annotated[str, Field(min_length=1, max_length=100)] = "India"
    latitude: Annotated[Decimal, Field(ge=-90, le=90)] | None = None
    longitude: Annotated[Decimal, Field(ge=-180, le=180)] | None = None
    employees: Annotated[int, Field(ge=0)] | None = None
    productionCapacity: NonNegativeDecimal | None = None
    productionUnit: Annotated[str, Field(max_length=50)] | None = None
    establishedYear: Annotated[int, Field(ge=1)] | None = None


class FactoryUpdate(ApiModel):
    name: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    industryType: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    description: str | None = None
    address: str | None = None
    city: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    state: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    country: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    latitude: Annotated[Decimal, Field(ge=-90, le=90)] | None = None
    longitude: Annotated[Decimal, Field(ge=-180, le=180)] | None = None
    employees: Annotated[int, Field(ge=0)] | None = None
    productionCapacity: NonNegativeDecimal | None = None
    productionUnit: Annotated[str, Field(max_length=50)] | None = None
    establishedYear: Annotated[int, Field(ge=1)] | None = None


class ManagerAssignment(ApiModel):
    manager: ManagerAccountCreate


class FactoryId(ApiModel):
    factoryId: UUID
