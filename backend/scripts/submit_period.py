import argparse
import asyncio
import os
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.schemas.user import UserContext, UserRole
from app.services.reporting import submit_reporting_period


async def submit(factory_id: UUID, period_id: UUID, user_id: UUID, email: str) -> int:
    settings = get_settings()
    if settings.database_url is None:
        print("DATABASE_URL is not configured")
        return 1
    os.environ.setdefault("DATABASE_URL", settings.database_url.get_secret_value())

    from app.core.database import db

    try:
        await db.connect()
        await submit_reporting_period(
            factory_id,
            period_id,
            UserContext(
                id=user_id,
                fullName="Pipeline Operator",
                email=email,
                role=UserRole.factory_owner,
            ),
            db,
        )
        print(f"Reporting period submitted: {period_id}")
        return 0
    except Exception as exc:
        print(f"Submission failed: {type(exc).__name__}: {exc}")
        return 1
    finally:
        if db.is_connected():
            await db.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit a reporting period for processing.")
    parser.add_argument("factory_id", type=UUID)
    parser.add_argument("period_id", type=UUID)
    parser.add_argument("user_id", type=UUID)
    parser.add_argument("email")
    arguments = parser.parse_args()
    return asyncio.run(
        submit(arguments.factory_id, arguments.period_id, arguments.user_id, arguments.email)
    )


if __name__ == "__main__":
    sys.exit(main())
