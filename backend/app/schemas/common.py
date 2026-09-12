from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

NonNegativeDecimal = Annotated[Decimal, Field(ge=0)]
Percentage = Annotated[Decimal, Field(ge=0, le=100)]
PositiveRank = Annotated[int, Field(gt=0)]


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, populate_by_name=True)


class AuditLogCreate(ApiModel):
    userId: UUID | None = None
    factoryId: UUID | None = None
    action: Annotated[str, Field(min_length=1, max_length=100)]
    entityType: Annotated[str, Field(min_length=1, max_length=100)]
    entityId: UUID | None = None
    metadata: dict[str, Any] | None = None
