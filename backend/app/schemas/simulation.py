from typing import Annotated, Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import ApiModel, NonNegativeDecimal, Percentage


class SimulationCreate(ApiModel):
    baseResultId: UUID
    name: Annotated[str, Field(min_length=1, max_length=200)]
    assumptions: dict[str, Any]
    baselineCo2e: NonNegativeDecimal
    resultingCo2e: NonNegativeDecimal
    co2Reduction: NonNegativeDecimal
    co2ReductionPercentage: Percentage
    estimatedCost: NonNegativeDecimal | None = None
    estimatedSavings: NonNegativeDecimal | None = None
    paybackMonths: NonNegativeDecimal | None = None
