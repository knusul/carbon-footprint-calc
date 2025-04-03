from pydantic import BaseModel

class EnergySource(BaseModel):
    energySourceId: str
    scopeId: str
    name: str
    conversionFactor: float
    emissionFactor: float

    class Config:
        min_anystr_length = 1  # To avoid errors when string values are empty
        str_min_length = True  # Strip leading and trailing whitespaces