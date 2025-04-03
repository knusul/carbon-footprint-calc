import json
from pathlib import Path
from typing import List, Dict
from fastapi import HTTPException
from app.models.carbon_footprint_request_payload import CarbonFootprintRequestPayload
from app.models.energy_source import EnergySource
from app.models.energy_scope import EnergyScope


class CalculateCarbonFootprint:

    def load_data(self, file_name: str):
        """ Load JSON data from the file. """
        path = Path(__file__).resolve().parent.parent / "mocks" / file_name
        with open(path, "r") as f:
            return json.load(f)

    def __init__(self, energy_sources: Dict[str, EnergySource] = None, scopes_data: List[dict] = None):
        self.ENERGY_SOURCES = energy_sources or {
            entry["energySourceId"]: EnergySource(**entry) for entry in self.load_data("energy_sources.json")
        }

        self.SCOPES_DATA = scopes_data or [
            EnergyScope(**scope) for scope in self.load_data("scopes.json")
        ]

        if not isinstance(self.SCOPES_DATA, list):
            raise ValueError("SCOPES_DATA should be a list, but it's not. Please check the scopes.json file.")

        for scope in self.SCOPES_DATA:
            if not scope.subScopes:
                raise ValueError(f"Missing 'subScopes' in scope: {scope.id}")

        # Create mapping for scopes (main scope level)
        self.SCOPE_MAP = {
            sub.id: {"name": scope.name, "label": scope.label}
            for scope in self.SCOPES_DATA for sub in scope.subScopes
        }

        # Create mapping for sub-scopes (the sub-scope level)
        self.SUB_SCOPE_MAP = {
            sub.id: sub
            for scope in self.SCOPES_DATA for sub in scope.subScopes
        }

    def calculate_co2_balance(self, energy_entries: List[CarbonFootprintRequestPayload]):
        """ Calculate CO2 balance based on energy entries. """
        scope_results = {}

        for energy_entry in energy_entries:
            energySource = self.ENERGY_SOURCES.get(energy_entry.energySourceId)
            if not energySource:
                raise HTTPException(status_code=400, detail=f"Invalid energySourceId: {energy_entry.energySourceId}")

            conversion_factor = energySource.conversionFactor
            emission_factor = energySource.emissionFactor
            scope_id = energySource.scopeId
            name = energySource.name

            # Use custom emission factor if provided
            effective_emission_factor = energy_entry.customEmissionFactor if energy_entry.customEmissionFactor is not None else emission_factor

            # Calculate values
            energy = round(energy_entry.consumption * conversion_factor, 5)
            co2 = round((energy * effective_emission_factor) / 1000, 5)

            # Find parent scope and sub-scope
            parent_scope = self.SCOPE_MAP.get(scope_id)
            sub_scope = self.SUB_SCOPE_MAP.get(scope_id)

            if not parent_scope or not sub_scope:
                raise ValueError("Scope data is missing parent_scope is {parent_scope} and sub_scope is {sub_scope}")            

            # Organize by main scope
            if parent_scope["name"] not in scope_results:
                scope_results[parent_scope["name"]] = {
                    "name": parent_scope["name"],
                    "label": parent_scope["label"],
                    "energy": 0,
                    "co2": 0,
                    "children": {}
                }

            # Organize by sub-scope
            if scope_id not in scope_results[parent_scope["name"]]["children"]:
                scope_results[parent_scope["name"]]["children"][scope_id] = {
                    "name": sub_scope.name,
                    "label": sub_scope.label,
                    "energy": 0,
                    "co2": 0,
                    "children": []
                }

            # Append entry as a child node
            entry_label = f"{name} ({energy_entry.description})"
            scope_results[parent_scope["name"]]["children"][scope_id]["children"].append({
                "name": sub_scope.name + ".1",  # Dynamic sub-sub-scope ID
                "label": entry_label,
                "energy": energy,
                "co2": co2,
                "children": []
            })

            # Accumulate values
            scope_results[parent_scope["name"]]["children"][scope_id]["energy"] += energy
            scope_results[parent_scope["name"]]["children"][scope_id]["co2"] += co2
            scope_results[parent_scope["name"]]["energy"] += energy
            scope_results[parent_scope["name"]]["co2"] += co2

        for scope in scope_results.values():
            scope["children"] = list(scope["children"].values())

        return list(scope_results.values())
