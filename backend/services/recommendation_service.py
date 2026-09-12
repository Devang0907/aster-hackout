from uuid import uuid4

from services.data_api import (
    get_resource,
    get_resource_by_id,
    create_resource
)

from recommendation_engine.main import run_recommendation_engine


async def generate_factory_recommendations(factory_id: str):

    # ----------------------------------
    # 1. Get factory data
    # ----------------------------------

    factory = await get_resource_by_id(
        "factories",
        factory_id
    )

    # ----------------------------------
    # 2. Get carbon results
    # ----------------------------------

    carbon_results = await get_resource(
        "carbon_results"
    )

    factory_results = [
        result
        for result in carbon_results
        if str(result.get("factory_id")) == str(factory_id)
    ]

    # ----------------------------------
    # 3. Build emissions dictionary
    # ----------------------------------

    emissions = {}

    for result in factory_results:

        source = result.get("source")

        if source:
            emissions[source] = result.get(
                "emission",
                result.get("co2", 0)
            )

    # Required fields expected by the engine
    emissions.setdefault("electricity", 0)
    emissions.setdefault("diesel", 0)
    emissions.setdefault("raw_material", 0)
    emissions.setdefault("waste", 0)
    emissions.setdefault("transport", 0)

    # ----------------------------------
    # 4. Rank emission sources
    # ----------------------------------

    ranked_sources = [
        {
            "source": source,
            "emission": value
        }
        for source, value in emissions.items()
    ]

    ranked_sources.sort(
        key=lambda x: x["emission"],
        reverse=True
    )

    # ----------------------------------
    # 5. Call existing recommendation engine
    # ----------------------------------

    recommendations = run_recommendation_engine(
        emissions,
        ranked_sources
    )

    # ----------------------------------
    # 6. Save recommendations
    # ----------------------------------

    saved_recommendations = []

    for recommendation in recommendations:

        data = {
            # Unique JSON Server record ID
            "id": str(uuid4()),

            # Original recommendation/intervention ID
            "intervention_id": recommendation.get("id"),

            "factory_id": factory_id,
            "factory_name": factory.get("name"),

            # Copy everything except original id
            **{
                key: value
                for key, value in recommendation.items()
                if key != "id"
            }
        }

        saved = await create_resource(
            "recommendations",
            data
        )

        saved_recommendations.append(saved)

    # ----------------------------------
    # 7. Return result to FastAPI
    # ----------------------------------

    return {
        "factory": factory,
        "emissions": emissions,
        "ranked_sources": ranked_sources,
        "recommendations": saved_recommendations
    }