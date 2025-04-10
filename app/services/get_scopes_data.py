import httpx
import os
from typing import List
from app.models.energy_scope import EnergyScope

def get_scopes_data() -> List[EnergyScope]:
    scopes_endpoint = os.getenv("SCOPES_ENDPOINT","http://localhost:8002")
    scopes_data_url = scopes_endpoint + "/scopes.json"

    response = httpx.get(scopes_data_url)

    if response.status_code == 200:
        json = response.json()
        return [EnergyScope(**entry) for entry in json]
    else:
        raise Exception(f"Failed to fetch scopes data: {response.status_code}, {response.text}")
