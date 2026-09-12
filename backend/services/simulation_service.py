from services.data_api import create_resource


async def save_simulation(data: dict):
    return await create_resource(
        "simulations",
        data
    )
