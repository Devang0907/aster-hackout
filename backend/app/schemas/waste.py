from typing import Annotated
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import ApiModel, NonNegativeDecimal


class WasteStreamCreate(ApiModel):
    reportingPeriodId: UUID
    wasteType: Annotated[str, Field(min_length=1, max_length=100)]
    quantity: NonNegativeDecimal
    unit: Annotated[str, Field(min_length=1, max_length=30)]
    treatmentMethod: Annotated[str, Field(max_length=100)] | None = None
    recycledQuantity: NonNegativeDecimal = 0
    recoveredQuantity: NonNegativeDecimal = 0
    disposedQuantity: NonNegativeDecimal = 0

    @model_validator(mode="after")
    def allocation_cannot_exceed_total(self) -> "WasteStreamCreate":
        allocated = self.recycledQuantity + self.recoveredQuantity + self.disposedQuantity
        if allocated > self.quantity:
            raise ValueError("recycled, recovered and disposed quantities exceed total quantity")
        return self
