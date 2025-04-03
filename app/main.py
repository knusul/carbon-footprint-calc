from fastapi import FastAPI
from typing import List
from app.models.carbon_footprint_request_payload import CarbonFootprintRequestPayload
from app.models.carbon_footprint_response import CarbonFootprintResponse
from app.services.calculate_carbon_footprint import CalculateCarbonFootprint

app = FastAPI()

@app.post("/carbon-footprint", response_model=List[CarbonFootprintResponse])
async def calculate_co2_balance(energy_sources: List[CarbonFootprintRequestPayload]):
    service = CalculateCarbonFootprint()
    result = service.calculate_co2_balance(energy_sources)
    return result