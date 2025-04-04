import httpx
import os
from typing import List, Dict

def get_energy_sources() -> List[Dict]:
    energy_sources_endpoint = os.getenv("ENERGY_SOURCES_ENDPOINT","http://localhost:8002")
    energy_sources_url = energy_sources_endpoint + "/energy_sources.json"

    response = httpx.get(energy_sources_url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch energy sources: {response.status_code}, {response.text}")
