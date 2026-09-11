import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings


async def check_database() -> int:
    settings = get_settings()
    if settings.database_url is None:
        print("DATABASE_URL is not configured")
        return 1

    os.environ.setdefault("DATABASE_URL", settings.database_url.get_secret_value())
    from app.core.database import db

    try:
        await db.connect()
        result = await db.query_raw("SELECT 1 AS ok")
        if not result or result[0].get("ok") != 1:
            print(f"Database query returned an unexpected result: {result}")
            return 1
        print("Database connection OK")
        return 0
    except Exception as exc:
        print(f"Database connection failed: {type(exc).__name__}: {exc}")
        return 1
    finally:
        if db.is_connected():
            await db.disconnect()


if __name__ == "__main__":
    sys.exit(asyncio.run(check_database()))
