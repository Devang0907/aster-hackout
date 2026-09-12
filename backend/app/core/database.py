from collections.abc import AsyncIterator

from prisma import Prisma

db = Prisma()


async def connect_database() -> None:
    if not db.is_connected():
        await db.connect()


async def disconnect_database() -> None:
    if db.is_connected():
        await db.disconnect()


async def get_database() -> AsyncIterator[Prisma]:
    """Yield the process-wide client; the app lifespan owns its connection."""
    yield db
