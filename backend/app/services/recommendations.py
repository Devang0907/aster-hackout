from typing import Any
from uuid import UUID

from app.schemas.recommendation import RecommendationStatus
from app.schemas.user import UserContext
from app.services.authorization import assert_factory_operational_access
from app.services.errors import NotFoundError


async def list_recommendations(
    factory_id: UUID, user: UserContext, database: Any
) -> list[Any]:
    await assert_factory_operational_access(user, factory_id, database)
    return await database.recommendation.find_many(
        where={"factoryId": str(factory_id)},
        include={
            "intervention": True,
            "material": True,
            "alternativeMaterial": True,
            "emissionSource": True,
        },
        order={"priority": "asc"},
    )


async def update_recommendation_status(
    factory_id: UUID,
    recommendation_id: UUID,
    status: RecommendationStatus,
    user: UserContext,
    database: Any,
) -> Any:
    await assert_factory_operational_access(user, factory_id, database)
    found = await database.recommendation.find_first(
        where={"id": str(recommendation_id), "factoryId": str(factory_id)}
    )
    if found is None:
        raise NotFoundError("recommendation not found")
    async with database.tx() as transaction:
        result = await transaction.recommendation.update(
            where={"id": str(recommendation_id)}, data={"status": status.value}
        )
        await transaction.auditlog.create(
            data={
                "userId": str(user.id),
                "factoryId": str(factory_id),
                "action": f"RECOMMENDATION_{status.value.upper()}",
                "entityType": "Recommendation",
                "entityId": str(recommendation_id),
            }
        )
    return result
