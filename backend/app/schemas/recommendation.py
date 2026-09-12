from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import ApiModel, NonNegativeDecimal, Percentage, PositiveRank


class InterventionCreate(ApiModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    category: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str, Field(min_length=1)]
    interventionType: Annotated[str, Field(max_length=100)] | None = None
    applicableIndustries: list[str] | dict[str, Any] | None = None
    estimatedCostMin: NonNegativeDecimal | None = None
    estimatedCostMax: NonNegativeDecimal | None = None
    expectedCo2ReductionPercentage: Percentage | None = None
    expectedEnergyReductionPercentage: Percentage | None = None
    expectedWasteReductionPercentage: Percentage | None = None
    paybackMonthsMin: NonNegativeDecimal | None = None
    paybackMonthsMax: NonNegativeDecimal | None = None
    feasibilityScore: Percentage | None = None
    technologyReadiness: Percentage | None = None
    implementationComplexity: Annotated[str, Field(max_length=50)] | None = None

    @model_validator(mode="after")
    def validate_ranges(self) -> "InterventionCreate":
        if self.estimatedCostMin is not None and self.estimatedCostMax is not None:
            if self.estimatedCostMax < self.estimatedCostMin:
                raise ValueError("estimatedCostMax must be at least estimatedCostMin")
        if self.paybackMonthsMin is not None and self.paybackMonthsMax is not None:
            if self.paybackMonthsMax < self.paybackMonthsMin:
                raise ValueError("paybackMonthsMax must be at least paybackMonthsMin")
        return self


class RecommendationStatus(StrEnum):
    new = "new"
    viewed = "viewed"
    accepted = "accepted"
    rejected = "rejected"
    implemented = "implemented"


class RecommendationCreate(ApiModel):
    resultId: UUID
    interventionId: UUID
    materialId: UUID | None = None
    alternativeMaterialId: UUID | None = None
    emissionSourceId: UUID | None = None
    priority: PositiveRank
    recommendationScore: Percentage | None = None
    estimatedCo2Reduction: NonNegativeDecimal | None = None
    estimatedCost: NonNegativeDecimal | None = None
    estimatedAnnualSavings: NonNegativeDecimal | None = None
    paybackMonths: NonNegativeDecimal | None = None
    feasibilityScore: Percentage | None = None
    confidenceScore: Percentage | None = None
    aiExplanation: str | None = None


class RecommendationStatusUpdate(ApiModel):
    status: RecommendationStatus
