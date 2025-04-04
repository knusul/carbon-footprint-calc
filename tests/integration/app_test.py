import pytest
import jwt
import os
from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv
from decimal import Decimal
from unittest.mock import patch


@pytest.fixture(scope="session", autouse=True)
def load_test_dotenv():
    load_dotenv(".env.test")


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def payload():
    return [
        {
            "description": "Standort Berlin",
            "energySourceId": "2007",
            "consumption": 1000.0
        },
        {
            "description": "Standort München",
            "energySourceId": "2004",
            "consumption": 4000.0,
            "customEmissionFactor": 0.25
        }
    ]


@pytest.fixture()
def valid_token():
    payload = {"sub": "test_user"}
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    return jwt.encode(payload, secret_key, algorithm=algorithm)


@pytest.mark.asyncio
async def test_calculate_co2_balance_authenticated(client, payload, valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}

    mocked_energy_sources = [{
        "energySourceId": "2007",
        "scopeId": "SCOPE_1_2",
        "name": "Diesel",
        "conversionFactor": "9.885",
        "emissionFactor": "0.25076"
    },
        {
        "energySourceId": "2004",
        "scopeId": "SCOPE_1_1",
        "name": "Erdgas",
        "conversionFactor": "1",
        "emissionFactor": "0.20226"
    },]

    mocked_scopes_data = [
        {
            "id": "SCOPE_1",
            "name": "Scope 1",
            "label": "Brenn-/Treibstoffe, Kältemittel, Prozessemissionen",
            "subScopes": [
                    {
                        "id": "SCOPE_1_1",
                        "name": "1.1",
                        "label": "Brennstoffe / Wärme"
                    },
                {
                        "id": "SCOPE_1_2",
                        "name": "1.2",
                        "label": "Treibstoffe für Mobilität/Flotte"
                    }
            ]
        },

    ]

    with patch("app.main.get_energy_sources", return_value=mocked_energy_sources), \
            patch("app.main.get_scopes_data", return_value=mocked_scopes_data):

        response = client.post("/carbon-footprint", json=payload, headers=headers)

        assert response.status_code == 200
        assert response.json() is not None


@pytest.mark.asyncio
async def test_calculate_co2_balance_unauthenticated(client, payload):
    response = client.post("/carbon-footprint", json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
