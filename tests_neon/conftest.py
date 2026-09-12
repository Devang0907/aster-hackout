import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))


# --------------------------------------------------
# Load .env BEFORE importing the FastAPI application
# --------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# Shared test data
# --------------------------------------------------

FACTORY_ID = os.getenv(
    "TEST_FACTORY_ID",
    "963b9cdf-7c11-48d6-98b0-904dbfe6b613",
)

EXPECTED_EMISSIONS = {
    "electricity": 35000.0,
    "diesel": 0.0,
    "raw_material": 92500.0,
    "transport": 255000.0,
    "waste": 500.0,
}

EXPECTED_TOTAL_CO2E = 383000.0


# Import only after paths + environment are configured.
from backend.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def calculated_payload(client):
    response = client.post(
        f"/api/emissions/{FACTORY_ID}/calculate"
    )
    assert response.status_code == 200, response.text
    return response.json()
