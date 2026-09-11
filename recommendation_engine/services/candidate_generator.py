from ..data.interventions import INTERVENTIONS

SOURCE_ALIASES = {
    "fuel": "diesel",
    "fuel_co2e": "diesel",
    "electricity_co2e": "electricity",
    "material_co2e": "raw_material",
    "transport_co2e": "transport",
    "waste_co2e": "waste",
}


def generate_candidates(ranked_sources, max_sources=3, interventions=None):

    candidates = []
    intervention_catalog = interventions or INTERVENTIONS

    # Take the most important emission sources
    important_sources = ranked_sources[:max_sources]

    for source_data in important_sources:

        source = source_data.get("source", source_data.get("sourceType", ""))
        source = SOURCE_ALIASES.get(source, source)

        for intervention_id, intervention in intervention_catalog.items():

            if intervention["source"] == source:

                candidate = {
                    "id": intervention_id,
                    **intervention
                }

                candidates.append(candidate)

    return candidates