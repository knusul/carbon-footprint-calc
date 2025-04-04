from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal
from typing import cast

class CarbonFootprintRequestPayload(BaseModel):
    description: str
    energySourceId: str
    consumption: Decimal
    customEmissionFactor: Optional[Decimal] = None

    @field_validator("consumption", "customEmissionFactor", mode="before")
    @classmethod
    def validate_decimal_places(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is None: 
            return value

        if isinstance(value, float):
            value = Decimal(str(value)) 
        elif isinstance(value, int):
            value = Decimal(value)
        elif not isinstance(value, Decimal):
            raise ValueError("Value must be a Decimal, float, or int")

        if cast(int, value.as_tuple().exponent) < -5:
            raise ValueError(f"{cls.__name__}: {value} must have a maximum of 5 decimal places")

        return value
