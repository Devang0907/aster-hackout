from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID


def to_prisma_data(value: Any) -> Any:
    """Convert API-layer scalar types while retaining Decimal/date precision."""
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (Decimal, date, datetime)):
        return value
    if isinstance(value, dict):
        return {key: to_prisma_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_prisma_data(item) for item in value]
    return value
