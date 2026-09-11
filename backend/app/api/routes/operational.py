from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import FactoryOperator
from app.core.database import get_database
from app.schemas.energy import EnergyUsageCreate
from app.schemas.logistics import LogisticsCreate
from app.schemas.material import MaterialUsageCreate
from app.schemas.waste import WasteStreamCreate
from app.services import operational as service

router = APIRouter(prefix="/factories/{factory_id}", tags=["operational-data"])
Database = Annotated[Any, Depends(get_database)]
ReportingPeriodFilter = Annotated[UUID | None, Query()]


@router.get("/material-usage")
async def list_material_usage(
    factory_id: UUID,
    current_user: FactoryOperator,
    database: Database,
    reporting_period_id: ReportingPeriodFilter = None,
) -> list[Any]:
    return await service.list_operational_records(
        "material", factory_id, current_user, database, reporting_period_id
    )


@router.post("/material-usage", status_code=201)
async def create_material_usage(
    factory_id: UUID,
    payload: MaterialUsageCreate,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    return await service.create_operational_record(
        "material", factory_id, payload, current_user, database
    )


@router.get("/energy-usage")
async def list_energy_usage(
    factory_id: UUID,
    current_user: FactoryOperator,
    database: Database,
    reporting_period_id: ReportingPeriodFilter = None,
) -> list[Any]:
    return await service.list_operational_records(
        "energy", factory_id, current_user, database, reporting_period_id
    )


@router.post("/energy-usage", status_code=201)
async def create_energy_usage(
    factory_id: UUID,
    payload: EnergyUsageCreate,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    return await service.create_operational_record(
        "energy", factory_id, payload, current_user, database
    )


@router.get("/waste-streams")
async def list_waste_streams(
    factory_id: UUID,
    current_user: FactoryOperator,
    database: Database,
    reporting_period_id: ReportingPeriodFilter = None,
) -> list[Any]:
    return await service.list_operational_records(
        "waste", factory_id, current_user, database, reporting_period_id
    )


@router.post("/waste-streams", status_code=201)
async def create_waste_stream(
    factory_id: UUID,
    payload: WasteStreamCreate,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    return await service.create_operational_record(
        "waste", factory_id, payload, current_user, database
    )


@router.get("/logistics")
async def list_logistics(
    factory_id: UUID,
    current_user: FactoryOperator,
    database: Database,
    reporting_period_id: ReportingPeriodFilter = None,
) -> list[Any]:
    return await service.list_operational_records(
        "logistics", factory_id, current_user, database, reporting_period_id
    )


@router.post("/logistics", status_code=201)
async def create_logistics(
    factory_id: UUID,
    payload: LogisticsCreate,
    current_user: FactoryOperator,
    database: Database,
) -> Any:
    return await service.create_operational_record(
        "logistics", factory_id, payload, current_user, database
    )
