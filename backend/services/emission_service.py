from services.json_api import get_resource


async def get_factory_emissions(factory_id: int):

    results = await get_resource("carbon_results")

    return [
        result
        for result in results
        if str(result.get("factory_id")) == str(factory_id)
    ]
