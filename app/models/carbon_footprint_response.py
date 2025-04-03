from pydantic import BaseModel
from typing import List, Dict

class CarbonFootprintResponse(BaseModel):
    name: str
    label: str
    energy: float
    co2: float
    children: List[Dict]