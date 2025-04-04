import httpx
import os

def get_scopes_data():
    scopes_endpoint = os.getenv("SCOPES_ENDPOINT","http://localhost:8002")
    scopes_data_url = scopes_endpoint + "/scopes.json"

    response = httpx.get(scopes_data_url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch scopes data: {response.status_code}, {response.text}")
