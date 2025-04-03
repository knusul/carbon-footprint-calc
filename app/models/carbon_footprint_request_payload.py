from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal

class CarbonFootprintRequestPayload(BaseModel):
    description: str
    energySourceId: str
    consumption: Decimal  # Use Decimal instead of float
    customEmissionFactor: Optional[Decimal] = None  # Use Decimal instead of float

    @field_validator("consumption", "customEmissionFactor", mode="before")
    @classmethod
    def validate_decimal_places(cls, value):
        if value is None:  # ✅ Allow None for optional fields
            return value

        if isinstance(value, float):
            value = Decimal(str(value))  # Convert to Decimal for precision
        elif not isinstance(value, Decimal):
            raise ValueError("Value must be a Decimal or float")

        if value.as_tuple().exponent < -5:  # More than 5 decimal places
            raise ValueError(f"{cls.__name__}: {value} must have a maximum of 5 decimal places")

        return value
