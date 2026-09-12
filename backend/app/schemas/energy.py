from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.schemas.common import ApiModel, NonNegativeDecimal, Percentage


class EnergyUsageCreate(ApiModel):
    reportingPeriodId: UUID
    energyType: Annotated[str, Field(min_length=1, max_length=100)]
    quantity: NonNegativeDecimal
    unit: Annotated[str, Field(min_length=1, max_length=30)]
    renewablePercentage: Percentage = 0
    source: Annotated[str, Field(max_length=100)] | None = None
