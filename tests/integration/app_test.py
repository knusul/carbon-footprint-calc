import pytest
from fastapi.testclient import TestClient
from app.main import app  # Import the FastAPI app from the app.main module
import json
from unittest.mock import mock_open, patch

@pytest.fixture()
def payload():
    return [
        {
            "description": "Standort Berlin",
            "energySourceId": "2007",
            "consumption": 1000
        },
        {
            "description": "Standort München",
            "energySourceId": "2004",
            "consumption": 4000,
            "customEmissionFactor": 0.25
        }
    ]

@pytest.mark.asyncio
async def test_calculate_co2_balance(payload):
    client = TestClient(app)

    response = client.post("/carbon-footprint", json=payload)

    assert response.status_code == 200