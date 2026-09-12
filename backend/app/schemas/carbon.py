from datetime import date, datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import ApiModel, NonNegativeDecimal, Percentage, PositiveRank


class ReportingPeriodStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ReportingPeriodCreate(ApiModel):
    periodStart: date
    periodEnd: date

    @model_validator(mode="after")
    def end_not_before_start(self) -> "ReportingPeriodCreate":
        if self.periodEnd < self.periodStart:
            raise ValueError("periodEnd must be on or after periodStart")
        return self


class EmissionFactorCreate(ApiModel):
    category: Annotated[str, Field(min_length=1, max_length=100)]
    activity: Annotated[str, Field(min_length=1, max_length=200)]
    factor: NonNegativeDecimal
    unit: Annotated[str, Field(min_length=1, max_length=50)]
    source: Annotated[str, Field(min_length=1)]
    sourceUrl: str | None = None
    region: Annotated[str, Field(max_length=100)] | None = None
    country: Annotated[str, Field(max_length=100)] | None = None
    version: Annotated[str, Field(min_length=1, max_length=50)]
    validFrom: date | None = None
    validUntil: date | None = None
    uncertaintyPercentage: Percentage | None = None

    @model_validator(mode="after")
    def valid_dates(self) -> "EmissionFactorCreate":
        if self.validFrom and self.validUntil and self.validUntil < self.validFrom:
            raise ValueError("validUntil must be on or after validFrom")
        return self


class CarbonResultCreate(ApiModel):
    reportingPeriodId: UUID
    pipelineRunId: UUID | None = None
    totalCo2e: NonNegativeDecimal
    electricityCo2e: NonNegativeDecimal = 0
    fuelCo2e: NonNegativeDecimal = 0
    materialCo2e: NonNegativeDecimal = 0
    transportCo2e: NonNegativeDecimal = 0
    wasteCo2e: NonNegativeDecimal = 0
    renewableOffset: NonNegativeDecimal = 0
    netCo2e: NonNegativeDecimal
    carbonIntensity: NonNegativeDecimal | None = None
    carbonIntensityUnit: Annotated[str, Field(max_length=100)] | None = None
    calculationVersion: Annotated[str, Field(min_length=1, max_length=50)]
    mlModelVersion: Annotated[str, Field(max_length=100)] | None = None
    calculatedAt: datetime | None = None

    @model_validator(mode="after")
    def ml_outputs_require_pipeline_trace(self) -> "CarbonResultCreate":
        if self.mlModelVersion is not None and self.pipelineRunId is None:
            raise ValueError("pipelineRunId is required when mlModelVersion is supplied")
        return self


class EmissionSeverity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EmissionSourceCreate(ApiModel):
    resultId: UUID
    sourceType: Annotated[str, Field(min_length=1, max_length=100)]
    sourceName: Annotated[str, Field(min_length=1, max_length=200)]
    sourceReferenceId: UUID | None = None
    emissionsCo2e: NonNegativeDecimal
    percentage: Percentage
    severity: EmissionSeverity
    rank: PositiveRank
    explanation: str | None = None


class PipelineRunStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class MlPipelineRunCreate(ApiModel):
    reportingPeriodId: UUID
    pipelineVersion: Annotated[str, Field(min_length=1, max_length=100)]
    modelVersion: Annotated[str, Field(max_length=100)] | None = None


class CarbonCreditResultCreate(ApiModel):
    reportingPeriodId: UUID
    grossEmissions: NonNegativeDecimal
    eligibleReductions: NonNegativeDecimal = 0
    verifiedReductions: NonNegativeDecimal = 0
    carbonCredits: NonNegativeDecimal = 0
    methodology: Annotated[str, Field(max_length=200)] | None = None
    verificationStatus: Annotated[str, Field(max_length=50)] | None = None
    calculatedAt: datetime | None = None
