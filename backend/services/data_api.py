# Database access facade for CarbonWise.
# Neon PostgreSQL is the only supported data backend.

from services.db_api import (
    get_resource,
    get_resource_by_id,
    create_resource,
    update_resource,
    delete_resource,
)

__all__ = [
    "get_resource",
    "get_resource_by_id",
    "create_resource",
    "update_resource",
    "delete_resource",
]
