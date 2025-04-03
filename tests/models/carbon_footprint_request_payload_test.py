import pytest
from pydantic import ValidationError
from decimal import Decimal
from app.models.carbon_footprint_request_payload import CarbonFootprintRequestPayload

def test_valid_consumption():
    entry = CarbonFootprintRequestPayload(
        description="Test Energy",
        energySourceId="ES123",
        consumption=Decimal("123.45678"),
        customEmissionFactor=Decimal("10.5")
    )
    assert entry.consumption == Decimal("123.45678")

def test_invalid_consumption_more_than_5_decimals():
    with pytest.raises(ValidationError, match="must have a maximum of 5 decimal places"):
        CarbonFootprintRequestPayload(
            description="Test Energy",
            energySourceId="ES123",
            consumption=Decimal("123.456789")
        )

def test_invalid_customEmissionFactor_more_than_5_decimals():
    with pytest.raises(ValidationError, match="must have a maximum of 5 decimal places"):
        CarbonFootprintRequestPayload(
            description="Test Energy",
            energySourceId="ES123",
            consumption=Decimal("12"),
            customEmissionFactor=Decimal("123.456789")
        )

def test_consumption_no_decimal():
    entry = CarbonFootprintRequestPayload(
        description="Test Energy",
        energySourceId="ES123",
        consumption=Decimal("100"),
    )
    assert entry.consumption == Decimal("100")

def test_optional_custom_emission_factor():
    entry = CarbonFootprintRequestPayload(
        description="Test Energy",
        energySourceId="ES123",
        consumption=Decimal("99.99999"),
        customEmissionFactor=None
    )
    assert entry.customEmissionFactor is None
