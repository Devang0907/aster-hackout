from .conftest import FACTORY_ID


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_factories_endpoint(client):
    response = client.get("/api/factories/")
    assert response.status_code == 200, response.text

    factories = response.json()
    assert isinstance(factories, list)
    assert len(factories) > 0

    assert any(
        str(factory.get("id")) == FACTORY_ID
        for factory in factories
    )


def test_factory_by_uuid(client):
    response = client.get(
        f"/api/factories/{FACTORY_ID}"
    )

    # If this is 422, check backend/api/factories.py.
    # The path parameter must be factory_id: str, not int.
    assert response.status_code == 200, (
        f"{response.status_code}: {response.text}\n"
        "If this is 422, change the factory route path parameter "
        "from int to str because factory IDs are UUIDs."
    )

    factory = response.json()
    assert str(factory["id"]) == FACTORY_ID
