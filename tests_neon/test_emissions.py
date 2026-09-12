from .conftest import (
    EXPECTED_EMISSIONS,
    EXPECTED_TOTAL_CO2E,
)


def test_emission_calculation(calculated_payload):
    result = calculated_payload[
        "emissions"
    ]["carbon_result"]

    assert float(result["total_co2e"]) == EXPECTED_TOTAL_CO2E
    assert float(result["net_co2e"]) == EXPECTED_TOTAL_CO2E

    assert float(result["electricity_co2e"]) == EXPECTED_EMISSIONS["electricity"]
    assert float(result["fuel_co2e"]) == EXPECTED_EMISSIONS["diesel"]
    assert float(result["material_co2e"]) == EXPECTED_EMISSIONS["raw_material"]
    assert float(result["transport_co2e"]) == EXPECTED_EMISSIONS["transport"]
    assert float(result["waste_co2e"]) == EXPECTED_EMISSIONS["waste"]


def test_emission_sources_ranked(calculated_payload):
    sources = calculated_payload[
        "emissions"
    ]["emission_sources"]

    assert len(sources) >= 5

    assert sources[0]["source_type"] == "transport"
    assert float(
        sources[0]["emissions_co2e"]
    ) == 255000.0
    assert sources[0]["rank"] == 1

    ranks = [
        source["rank"]
        for source in sources
    ]

    assert ranks == sorted(ranks)


def test_percentages_sum_to_approximately_100(
    calculated_payload
):
    sources = calculated_payload[
        "emissions"
    ]["emission_sources"]

    total_percentage = sum(
        float(source["percentage"])
        for source in sources
    )

    assert abs(
        total_percentage - 100.0
    ) < 0.02
