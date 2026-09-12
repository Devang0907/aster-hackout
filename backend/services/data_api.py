from config import DATA_BACKEND


if DATA_BACKEND == "json":

    from services.json_api import (
        get_resource,
        get_resource_by_id,
        create_resource,
        update_resource,
        delete_resource
    )

elif DATA_BACKEND == "db":

    from services.db_api import (
        get_resource,
        get_resource_by_id,
        create_resource,
        update_resource,
        delete_resource
    )

else:

    raise ValueError(
        f"Unknown DATA_BACKEND: {DATA_BACKEND}"
    )