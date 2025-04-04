import json
from pathlib import Path
from typing import List, Dict
from app.models.carbon_footprint_request_payload import CarbonFootprintRequestPayload
from app.models.energy_source import EnergySource
from app.models.energy_scope import EnergyScope
from decimal import Decimal

class CalculateCarbonFootprint:
    def __init__(self, energy_sources: Dict[str, EnergySource] = None, scopes_data: List[dict] = None):
        self.ENERGY_SOURCES = {
            entry["energySourceId"]: EnergySource(**entry) for entry in energy_sources or self.load_data("energy_sources.json")
        }

        self.SCOPES_DATA = [
            EnergyScope(**scope) for scope in scopes_data or self.load_data("scopes.json")
        ]

        if not isinstance(self.SCOPES_DATA, list):
            raise ValueError(
                "SCOPES_DATA should be a list, but it's not. Please check the scopes.json file.")

        for scope in self.SCOPES_DATA:
            if not scope.subScopes:
                raise ValueError(f"Missing 'subScopes' in a scope: {scope.id}")

        # Build the tree of scopes
        self.SCOPE_TREE = self._build_scope_tree(self.SCOPES_DATA)

    def load_data(self, file_name: str):
        """ Load JSON data from the file. """
        path = Path(__file__).resolve().parent.parent / "mocks" / file_name
        with open(path, "r") as f:
            return json.load(f)

    def _build_scope_tree(self, scopes_data: List['EnergyScope']) -> List[Dict]:
        """
        Recursively build the tree structure for scopes from the scopes_data.
        Assumes scopes don't have cycles

        Returns:
        List[Dict]: A list of dictionaries representing the root-level scopes with their sub-scopes.
        """
        scope_map = []

        # Iterate over each scope in the input list
        for scope in scopes_data:
            scope_node = {
                "id": scope.id,
                "name": scope.name,
                "label": scope.label,
                "energy": 0,
                "co2": 0,
                "children": []
            }

            for sub_scope in scope.subScopes:
                scope_node["children"].append({
                    "parent": scope_node,
                    "id": sub_scope.id,
                    "name": sub_scope.name,
                    "label": sub_scope.label,
                    "energy": 0,
                    "co2": 0,
                    "children": []
                })

            scope_map.append(scope_node)

        return scope_map

    def find_child_by_id(self, tree, target_id):
        """
        Recursively traverse the list of root-level scopes (trees) to find a child with the given target_id.
        This version supports a list of trees, where each root node is in the 'tree' list.
        """
        for root in tree:
            if root["id"] == target_id:
                return root

            stack = [root]
            while stack:
                node = stack.pop()
                if "id" in node and node["id"] == target_id:
                    return node
                if "children" in node:
                    stack.extend(node["children"])

        return None

    def _assign_energy_entry(self, entry, tree, energy_source_name):
        """
        Assigns the energy and CO2 values by creating a new child node in the appropriate sub-scope.
        """
        node = self.find_child_by_id(tree, entry["scope_id"])
        new_name = f"{node['name']}.{len(node['children']) + 1}"
        new_child = {
            "name": new_name,
            "label": f"{energy_source_name} ({entry['description']})",
            "energy": entry["energy"],
            "co2": entry["co2"],
            "children": []
        }

        node["children"].append(new_child)

        # Propagate summed values to parent nodes
        parent_scope = node
        while parent_scope:
            parent_scope["energy"] += entry["energy"]
            parent_scope["co2"] += entry["co2"]
            parent_scope = parent_scope.get("parent")

    def calculate_co2_balance(self, energy_entries: List[CarbonFootprintRequestPayload]):
        """ Calculate CO2 balance based on energy entries. """

        for energy_entry in energy_entries:
            # Get energy source details
            energySource = self.ENERGY_SOURCES.get(energy_entry.energySourceId)
            if not energySource: # TODO: invalid input generates 500 but should be handled gracefully
                raise ValueError(
                f"Invalid energySourceId: {energy_entry.energySourceId}")
            conversion_factor = Decimal(energySource.conversionFactor)
            emission_factor = Decimal(energySource.emissionFactor)
            scope_id = energySource.scopeId
            name = energySource.name

            # Use custom emission factor if provided
            effective_emission_factor = energy_entry.customEmissionFactor if energy_entry.customEmissionFactor is not None else emission_factor

            # Calculate values
            energy = round(energy_entry.consumption * conversion_factor, 5)
            co2 = round((energy * effective_emission_factor) / 1000, 5)

            # Assign energy and CO2 values to the appropriate node in the tree
            energy_entry_data = {
                "scope_id": scope_id,
                "energy": energy,
                "co2": co2,
                "description": energy_entry.description
            }
            self._assign_energy_entry(energy_entry_data, self.SCOPE_TREE, name)

        return self.convert_scope_tree(self.SCOPE_TREE)

    def convert_scope_tree(self, tree):
        # TODO use serializer instead
        for node in tree:
            node.pop("id", None)
            node.pop("parent", None)
            node["children"] = self.convert_scope_tree(node["children"])

        return tree
