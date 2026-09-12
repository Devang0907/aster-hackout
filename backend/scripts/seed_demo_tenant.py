import asyncio
import importlib.util
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings

SEED_PATH = Path(__file__).resolve().parents[1] / "prisma" / "seed.py"
SEED_SPEC = importlib.util.spec_from_file_location("demo_seed", SEED_PATH)
if SEED_SPEC is None or SEED_SPEC.loader is None:
    raise RuntimeError("could not load seed module")
SEED_MODULE = importlib.util.module_from_spec(SEED_SPEC)
SEED_SPEC.loader.exec_module(SEED_MODULE)


async def main() -> None:
    settings = get_settings()
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not configured")
    os.environ.setdefault("DATABASE_URL", settings.database_url.get_secret_value())
    from app.core.database import db

    await db.connect()
    try:
        materials = await db.material.find_many()
        material_ids = {material.materialCode: material.id for material in materials}
        required = set(SEED_MODULE.MATERIALS)  # type: ignore[attr-defined]
        missing = [code for code, *_ in required if code not in material_ids]
        if missing:
            raise RuntimeError(f"missing seeded materials: {missing}")
        await SEED_MODULE.seed_demo_tenant(db, material_ids)
        print("Demo tenant seeded")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
