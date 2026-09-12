import argparse
import asyncio
import os
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.services.pipeline import run_reporting_period_pipeline


async def run(factory_id: UUID, period_id: UUID) -> int:
    settings = get_settings()
    if settings.database_url is None:
        print("DATABASE_URL is not configured")
        return 1
    os.environ.setdefault("DATABASE_URL", settings.database_url.get_secret_value())

    from app.core.database import db

    try:
        await db.connect()
        result = await run_reporting_period_pipeline(factory_id, period_id, db)
        print(f"Pipeline completed: carbon result {result.id}")
        return 0
    except Exception as exc:
        print(f"Pipeline failed: {type(exc).__name__}: {exc}")
        return 1
    finally:
        if db.is_connected():
            await db.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate a reporting period and persist recommendations."
    )
    parser.add_argument("factory_id", type=UUID)
    parser.add_argument("period_id", type=UUID)
    arguments = parser.parse_args()
    return asyncio.run(run(arguments.factory_id, arguments.period_id))


if __name__ == "__main__":
    sys.exit(main())
