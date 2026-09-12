import httpx


BASE_URL = "http://localhost:3000"

FACTORY_ID = "33333333-3333-3333-3333-333333333333"

EXPECTED_RESOURCES = [
    "users",
    "factories",
    "reporting_periods",
    "materials",
    "material_alternatives",
    "factory_material_usage",
    "energy_usage",
    "waste_streams",
    "logistics",
    "emission_factors",
    "carbon_results",
    "emission_sources",
    "interventions",
    "recommendations",
    "simulations",
    "ml_pipeline_runs",
    "carbon_credit_results",
    "audit_logs",
]


def test_json_server_running():
    response = httpx.get(BASE_URL)

    assert response.status_code == 200


def test_get_factories():
    response = httpx.get(
        f"{BASE_URL}/factories"
    )

    assert response.status_code == 200

    factories = response.json()

    assert isinstance(factories, list)
    assert len(factories) > 0


def test_get_factory_by_uuid():
    response = httpx.get(
        f"{BASE_URL}/factories/{FACTORY_ID}"
    )

    assert response.status_code == 200

    factory = response.json()

    assert factory["id"] == FACTORY_ID
    assert factory["name"] == "Demo Manufacturing Plant"


def test_expected_resources_exist():

    for resource in EXPECTED_RESOURCES:

        response = httpx.get(
            f"{BASE_URL}/{resource}"
        )

        assert response.status_code == 200, (
            f"Resource failed: {resource}"
        )


def test_seeded_carbon_results():

    response = httpx.get(
        f"{BASE_URL}/carbon_results"
    )

    assert response.status_code == 200

    results = response.json()

    factory_results = [
        result
        for result in results
        if str(result.get("factory_id")) == FACTORY_ID
    ]

    assert len(factory_results) >= 5

    emissions = {
        result["source"]: result["emission"]
        for result in factory_results
    }

    assert emissions["electricity"] == 35000
    assert emissions["diesel"] == 10000
    assert emissions["raw_material"] == 3000
    assert emissions["waste"] == 500
    assert emissions["transport"] == 1000


def test_json_server_crud():

    data = {
        "type": "pytest",
        "message": "temporary test record"
    }

    # -------------------------
    # CREATE
    # -------------------------

    response = httpx.post(
        f"{BASE_URL}/audit_logs",
        json=data
    )

    assert response.status_code in (200, 201)

    created = response.json()

    assert "id" in created

    test_id = created["id"]


    # -------------------------
    # READ
    # -------------------------

    response = httpx.get(
        f"{BASE_URL}/audit_logs/{test_id}"
    )

    assert response.status_code == 200

    record = response.json()

    assert str(record["id"]) == str(test_id)

    assert record["message"] == "temporary test record"


    # -------------------------
    # UPDATE
    # -------------------------

    updated_data = {
        "type": "pytest",
        "message": "updated test record"
    }

    response = httpx.put(
        f"{BASE_URL}/audit_logs/{test_id}",
        json=updated_data
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["message"] == "updated test record"


    # -------------------------
    # DELETE
    # -------------------------

    response = httpx.delete(
        f"{BASE_URL}/audit_logs/{test_id}"
    )

    assert response.status_code in (200, 204)


    # -------------------------
    # VERIFY DELETE
    # -------------------------

    response = httpx.get(
        f"{BASE_URL}/audit_logs/{test_id}"
    )

    assert response.status_code == 404