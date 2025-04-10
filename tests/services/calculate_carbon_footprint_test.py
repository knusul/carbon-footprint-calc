import pytest
from app.services.calculate_carbon_footprint import CalculateCarbonFootprint
from app.models.carbon_footprint_request_payload import CarbonFootprintRequestPayload
from app.models.energy_source import EnergySource
from decimal import Decimal


@pytest.fixture()
def payload():
    return [
        CarbonFootprintRequestPayload(
            energySourceId="2007",
            consumption=Decimal(1000),
            description="Standort Berlin"
        ),
        CarbonFootprintRequestPayload(
            energySourceId="2004",
            consumption=Decimal(4000),
            customEmissionFactor=0.25,
            description="Standort München"
        ),
        CarbonFootprintRequestPayload(
            energySourceId="4005",
            consumption=Decimal(10000),
            description="Flug nach Thailand"
        )
    ]


@pytest.fixture()
def expected_response():
    return [
        {
            "name": "Scope 1",
            "label": "Brenn-/Treibstoffe, Kältemittel, Prozessemissionen",
            "energy": 14000.0,
            "co2": 3.5,
            "children": [
                {
                    "name": "1.1",
                    "label": "Brennstoffe / Wärme",
                    "energy": 4000.0,
                    "co2": 1.0,
                    "children": [
                        {
                            "name": "1.1.1",
                            "label": "Erdgas (Standort München)",
                            "energy": 4000.0,
                            "co2": 1.0,
                            "children": [],
                        }
                    ],
                },
                {
                    "name": "1.2",
                    "label": "Treibstoffe für Mobilität/Flotte",
                    "energy": 10000.0,
                    "co2": 2.5,
                    "children": [
                        {
                            "name": "1.2.1",
                            "label": "Diesel (Standort Berlin)",
                            "energy": 10000.0,
                            "co2": 2.5,
                            "children": [],
                        }
                    ],
                },
            ],
        },
        {
            "name": "Scope 2",
            "label": "Bezogene Energien",
            "energy": 0,
            "co2": 0,
            "children": [
                {
                    "name": "2.1",
                    "label": "Strom inkl. E-Flotte",
                    "energy": 0,
                    "co2": 0,
                    "children": [],
                },
                {
                    "name": "2.2",
                    "label": "Fernwärme/-kälte",
                    "energy": 0,
                    "co2": 0,
                    "children": [],
                },
                {
                    "name": "2.3",
                    "label": "Ferndampf",
                    "energy": 0,
                    "co2": 0,
                    "children": [],
                },
            ],
        },
        {
            "name": "Scope 3",
            "label": "Vor- und nachgelagerte Wertschöpfungskette",
            "energy": 10000.0,
            "co2": 2.0,
            "children": [
                {
                    "name": "3.6",
                    "label": "Dienstreisen",
                    "energy": 10000.0,
                    "co2": 2.0,
                    "children": [
                        {
                            "name": "3.6.1",
                            "label": "Flugzeug (Business Class) (Flug nach Thailand)",
                            "energy": 10000.0,
                            "co2": 2.0,
                            "children": [],
                        }
                    ],
                }
            ],
        },
    ]


@pytest.fixture()
def mock_carbon_footprint_service():
    mock_energy_sources = [
        {
            "energySourceId": "2007",
            "scopeId": "SCOPE_1_2",
            "name": "Diesel",
            "conversionFactor": "10",
            "emissionFactor": "0.25"
        },
        {
            "energySourceId": "2004",
            "scopeId": "SCOPE_1_1",
            "name": "Erdgas",
            "conversionFactor": "1",
            "emissionFactor": "0.2"
        },
        {
            "energySourceId": "4005",
            "scopeId": "SCOPE_3_6",
            "name": "Flugzeug (Business Class)",
            "conversionFactor": "1",
            "emissionFactor": "0.2"
        }
    ]

    return CalculateCarbonFootprint(energy_sources=mock_energy_sources)


def test_calculate_carbon_footprint(mock_carbon_footprint_service, payload, expected_response):
    result = mock_carbon_footprint_service.calculate_co2_balance(payload)
    assert result == expected_response


def test_throws_error_when_energy_source_id_does_not_exist(mock_carbon_footprint_service):
    payload = [
        CarbonFootprintRequestPayload(
            energySourceId="999999",
            consumption=Decimal(1000),
            description="Standort Berlin"
        ),
    ]

    with pytest.raises(ValueError, match="Invalid energySourceId: 999999"):
        mock_carbon_footprint_service.calculate_co2_balance(payload)
