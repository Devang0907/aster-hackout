from typing import Annotated, Any
from uuid import UUID

from pydantic import Field, model_validator

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

    @model_validator(mode="after")
    def values_are_consistent(self) -> "SimulationCreate":
        expected_reduction = self.baselineCo2e - self.resultingCo2e
        if expected_reduction < 0 or self.co2Reduction != expected_reduction:
            raise ValueError("co2Reduction must equal baselineCo2e minus resultingCo2e")
        if self.baselineCo2e == 0:
            if self.co2ReductionPercentage != 0:
                raise ValueError("co2ReductionPercentage must be zero for a zero baseline")
        elif self.co2ReductionPercentage != self.co2Reduction / self.baselineCo2e * 100:
            raise ValueError("co2ReductionPercentage does not match co2Reduction")
        return self
