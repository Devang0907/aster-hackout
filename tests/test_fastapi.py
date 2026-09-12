import httpx


BASE_URL = "http://localhost:8000"

FACTORY_ID = (
    "33333333-3333-3333-3333-333333333333"
)


def test_fastapi_root():

    response = httpx.get(
        f"{BASE_URL}/"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["message"]
        == "CarbonWise API is running"
    )


def test_fastapi_health():

    response = httpx.get(
        f"{BASE_URL}/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_fastapi_factories():

    response = httpx.get(
        f"{BASE_URL}/api/factories/"
    )

    assert response.status_code == 200

    factories = response.json()

    assert isinstance(factories, list)
    assert len(factories) > 0


def test_fastapi_factory_by_uuid():

    response = httpx.get(
        f"{BASE_URL}/api/factories/{FACTORY_ID}"
    )

    assert response.status_code == 200

    factory = response.json()

    assert factory["id"] == FACTORY_ID


def test_fastapi_recommendations():

    response = httpx.get(
        f"{BASE_URL}/api/recommendations/{FACTORY_ID}",
        timeout=30
    )

    assert response.status_code == 200

    data = response.json()

    assert "factory" in data
    assert "emissions" in data
    assert "ranked_sources" in data
    assert "recommendations" in data

    assert (
        data["factory"]["id"]
        == FACTORY_ID
    )

    assert (
        data["emissions"]["electricity"]
        == 35000
    )

    assert (
        data["emissions"]["diesel"]
        == 10000
    )

    assert (
        len(data["recommendations"])
        <= 3
    )

    assert (
        len(data["recommendations"])
        > 0
    )