from pydantic import BaseModel
from typing import List

class SubScope(BaseModel):
    id: str
    name: str
    label: str

class EnergyScope(BaseModel):
    id: str
    name: str
    label: str
    subScopes: List[SubScope]
