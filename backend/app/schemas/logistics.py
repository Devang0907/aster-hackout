from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.schemas.common import ApiModel, NonNegativeDecimal


class LogisticsCreate(ApiModel):
    reportingPeriodId: UUID
    transportType: Annotated[str, Field(min_length=1, max_length=100)]
    mode: Annotated[str, Field(min_length=1, max_length=50)]
    distanceKm: NonNegativeDecimal
    weightTonnes: NonNegativeDecimal | None = None
    trips: Annotated[int, Field(ge=0)] | None = None
    fuelType: Annotated[str, Field(max_length=50)] | None = None
