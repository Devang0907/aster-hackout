from ..data.interventions import INTERVENTIONS


def generate_candidates(ranked_sources, max_sources=3):

    candidates = []

    # Take the most important emission sources
    important_sources = ranked_sources[:max_sources]

    for source_data in important_sources:

        source = source_data["source"]

        for intervention_id, intervention in INTERVENTIONS.items():

            if intervention["source"] == source:

                candidate = {
                    "id": intervention_id,
                    **intervention
                }

                candidates.append(candidate)

    return candidates