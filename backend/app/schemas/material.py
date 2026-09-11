from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import ApiModel, NonNegativeDecimal, Percentage


class MaterialCreate(ApiModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    materialCode: Annotated[str, Field(max_length=50)] | None = None
    materialType: Annotated[str, Field(min_length=1, max_length=100)]
    category: Annotated[str, Field(max_length=100)] | None = None
    subcategory: Annotated[str, Field(max_length=100)] | None = None
    grade: Annotated[str, Field(max_length=100)] | None = None
    description: str | None = None
    carbonFactor: NonNegativeDecimal | None = None
    carbonUnit: Annotated[str, Field(max_length=50)] | None = None
    carbonFactorSource: str | None = None
    carbonFactorVersion: Annotated[str, Field(max_length=50)] | None = None
    recycledContentPossible: bool = False
    recyclable: bool = False
    hazardous: bool = False
    sustainabilityScore: Percentage | None = None


class MaterialAlternativeCreate(ApiModel):
    materialId: UUID
    alternativeMaterialId: UUID
    substitutionPercentage: Percentage | None = None
    carbonReductionPercentage: Percentage | None = None
    costDifferencePercentage: Percentage | None = None
    availabilityScore: Percentage | None = None
    compatibilityScore: Percentage | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def materials_must_differ(self) -> "MaterialAlternativeCreate":
        if self.materialId == self.alternativeMaterialId:
            raise ValueError("a material cannot be its own alternative")
        return self


class MaterialUsageCreate(ApiModel):
    reportingPeriodId: UUID
    materialId: UUID
    quantity: NonNegativeDecimal
    unit: Annotated[str, Field(min_length=1, max_length=30)]
    recycledPercentage: Percentage = 0
    supplierName: Annotated[str, Field(max_length=200)] | None = None
