from fastapi import APIRouter, HTTPException

from services.data_api import (
    get_resource,
    get_resource_by_id,
    create_resource,
    update_resource,
    delete_resource
)

router = APIRouter(
    prefix="/api/factories",
    tags=["Factories"]
)


@router.get("/")
async def get_factories():
    return await get_resource("factories")


@router.get("/{factory_id}")
async def get_factory(factory_id: str):

    try:
        return await get_resource_by_id(
            "factories",
            factory_id
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Factory not found"
        )


@router.post("/")
async def create_factory(factory: dict):

    return await create_resource(
        "factories",
        factory
    )


@router.put("/{factory_id}")
async def update_factory(
    factory_id: str,
    factory: dict
):

    return await update_resource(
        "factories",
        factory_id,
        factory
    )


@router.delete("/{factory_id}")
async def delete_factory(factory_id: str):

    await delete_resource(
        "factories",
        factory_id
    )

    return {
        "message": "Factory deleted successfully"
    }
