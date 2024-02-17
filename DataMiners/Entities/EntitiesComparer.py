from typing import Any

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.Entities, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Entities:
    behavior_packs:DataMinerTyping.BehaviorPacks = dependencies["behavior_packs"]
    if behavior_packs is None:
        behavior_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    def fix_weird_components(entity_name:str, entity_behavior_packs:dict[str,Any]) -> dict[str,Any]:
        # deletes components that are, for some reason, outside of the "components" or "component_groups" keys
        for behavior_pack_name, entity_data in entity_behavior_packs.items():
            for key_to_delete in [key for key in entity_data["minecraft:entity"] if key.startswith("minecraft:")]:
                del entity_data["minecraft:entity"][key_to_delete]
            # MCPE-178417
            if "events" in entity_data["minecraft:entity"]:
                for event in entity_data["minecraft:entity"]["events"]:
                    if "remove" not in entity_data["minecraft:entity"]["events"][event]: continue
                    for key_to_delete in [key for key in entity_data["minecraft:entity"]["events"][event]["remove"].keys() if key.startswith("minecraft:")]:
                        del entity_data["minecraft:entity"]["events"][event]["remove"][key_to_delete]
        return entity_behavior_packs
    return {entity_name: fix_weird_components(entity_name, CollapseResourcePacks.collapse_resource_packs(entity_behavior_packs, behavior_packs)) for entity_name, entity_behavior_packs in data.items()}

def behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

comparer = ComparerImporter.load_from_file("entities", {
    "normalize": normalize,
    "behavior_pack_comparison_move_function": behavior_pack_comparison_move_function,
})
