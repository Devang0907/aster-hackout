from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from prisma.errors import PrismaError

from app.api.dependencies import FactoryOperator
from app.core.database import get_database
from app.schemas.carbon import ReportingPeriodCreate
from app.services import reporting as service

router = APIRouter(prefix="/factories/{factory_id}/reporting-periods", tags=["reporting"])
Database = Annotated[Any, Depends(get_database)]


@router.get("")
async def list_periods(
    factory_id: UUID, current_user: FactoryOperator, database: Database
) -> list[Any]:
    return await service.list_reporting_periods(factory_id, current_user, database)


@router.post("", status_code=201)
async def create_period(
    factory_id: UUID,
    payload: ReportingPeriodCreate,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    try:
        return await service.create_reporting_period(factory_id, payload, current_user, database)
    except PrismaError as exc:
        raise HTTPException(
            status_code=503,
            detail="Reporting data could not be stored. Check the database connection and schema.",
        ) from exc


@router.post("/{period_id}/submit")
async def submit_period(
    factory_id: UUID,
    period_id: UUID,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    return await service.submit_reporting_period(
        factory_id, period_id, current_user, database
    )
