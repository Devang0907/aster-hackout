import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not configured")
    os.environ.setdefault("DATABASE_URL", settings.database_url.get_secret_value())
    from app.core.database import db

    await db.connect()
    try:
        for name, delegate in (
            ("users", db.user),
            ("factories", db.factory),
            ("periods", db.reportingperiod),
            ("interventions", db.intervention),
            ("factors", db.emissionfactor),
            ("pipeline_runs", db.mlpipelinerun),
            ("carbon_results", db.carbonresult),
            ("emission_sources", db.emissionsource),
            ("recommendations", db.recommendation),
        ):
            rows = await delegate.find_many()
            print(f"{name}: {len(rows)}")
            for row in rows[:3]:
                status = getattr(row, "status", None)
                print(f"  {row.id}" + (f" status={status}" if status is not None else ""))
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
