import os

import psycopg


EXPECTED_TABLES = {
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
    "ml_pipeline_runs",
    "carbon_results",
    "emission_sources",
    "interventions",
    "recommendations",
    "simulations",
    "carbon_credit_results",
    "audit_logs",
}


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    assert database_url, (
        "DATABASE_URL is not set. "
        "Make sure your project-root .env contains DATABASE_URL."
    )
    return database_url


def test_neon_connection():
    with psycopg.connect(get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            assert cur.fetchone()[0] == 1


def test_expected_tables_exist():
    with psycopg.connect(get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
            tables = {row[0] for row in cur.fetchall()}

    missing = EXPECTED_TABLES - tables
    assert not missing, f"Missing tables: {sorted(missing)}"


def test_factory_exists_in_neon():
    from .conftest import FACTORY_ID

    with psycopg.connect(get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM factories WHERE id = %s",
                (FACTORY_ID,),
            )
            row = cur.fetchone()

    assert row is not None, f"Factory {FACTORY_ID} does not exist in Neon"
