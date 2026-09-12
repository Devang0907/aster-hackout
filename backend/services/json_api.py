import httpx
from config import JSON_SERVER_URL


async def get_resource(resource: str):
    url = f"{JSON_SERVER_URL}/{resource}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_resource_by_id(resource: str, item_id):
    url = f"{JSON_SERVER_URL}/{resource}/{item_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def create_resource(resource: str, data: dict):
    url = f"{JSON_SERVER_URL}/{resource}"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
        return response.json()


async def update_resource(resource: str, item_id, data: dict):
    url = f"{JSON_SERVER_URL}/{resource}/{item_id}"

    async with httpx.AsyncClient() as client:
        response = await client.put(url, json=data)
        response.raise_for_status()
        return response.json()


async def delete_resource(resource: str, item_id):
    url = f"{JSON_SERVER_URL}/{resource}/{item_id}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
        response.raise_for_status()
        return True
