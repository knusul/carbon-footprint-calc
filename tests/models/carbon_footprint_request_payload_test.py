import pytest
from pydantic import ValidationError
from app.models.carbon_footprint_request_payload import CarbonFootprintRequestPayload

def test_valid_consumption():
    entry = CarbonFootprintRequestPayload(
        description="Test Energy",
        energySourceId="ES123",
        consumption=123.45678,  # Exactly 5 decimal places
        customEmissionFactor=10.5
    )
    assert entry.consumption == 123.45678 

def test_invalid_consumption_more_than_5_decimals():
    with pytest.raises(ValidationError, match="consumption must have a maximum of 5 decimal places"):
        CarbonFootprintRequestPayload(
            description="Test Energy",
            energySourceId="ES123",
            consumption=123.456789,  # 6 decimal places (should fail)
        )

def test_consumption_no_decimal():
    entry = CarbonFootprintRequestPayload(
        description="Test Energy",
        energySourceId="ES123",
        consumption=100,
    )
    assert entry.consumption == 100

def test_optional_custom_emission_factor():
    entry = CarbonFootprintRequestPayload(
        description="Test Energy",
        energySourceId="ES123",
        consumption=99.99999,
        customEmissionFactor=None
    )
    assert entry.customEmissionFactor is None
