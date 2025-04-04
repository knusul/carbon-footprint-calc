import httpx
import os
from typing import List
from app.models.energy_source import EnergySource


def get_energy_sources() -> List[EnergySource]:
    energy_sources_endpoint = os.getenv(
        "ENERGY_SOURCES_ENDPOINT", "http://localhost:8002")
    energy_sources_url = energy_sources_endpoint + "/energy_sources.json"

    response = httpx.get(energy_sources_url)

    if response.status_code == 200:
        json_data = response.json()
        return [EnergySource(**entry) for entry in json_data]

    else:
        raise Exception(
            f"Failed to fetch energy sources: {response.status_code}, {response.text}")
