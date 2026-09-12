from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_database

router = APIRouter(tags=["health"])
Database = Annotated[Any, Depends(get_database)]


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
async def database_health(database: Database) -> dict[str, str]:
    try:
        await database.query_raw("SELECT 1 AS ok")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"status": "ok"}
