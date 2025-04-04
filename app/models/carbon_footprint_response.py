from __future__ import annotations
from pydantic import BaseModel
from typing import List


class CarbonFootprintResponse(BaseModel):
    name: str
    label: str
    energy: float
    co2: float
    children: List[CarbonFootprintResponse] = []