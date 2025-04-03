from pydantic import BaseModel, field_validator
from typing import Optional

class CarbonFootprintRequestPayload(BaseModel):
    description: str
    energySourceId: str
    consumption: float  # Max 5 decimal places
    customEmissionFactor: Optional[float] = None  # Optional

    @field_validator("consumption")
    @classmethod
    def validate_decimal_places(cls, value):
        if isinstance(value, float):
            decimal_part = str(value).split(".")[-1]
            if len(decimal_part) > 5:
                raise ValueError("consumption must have a maximum of 5 decimal places")
        return value
