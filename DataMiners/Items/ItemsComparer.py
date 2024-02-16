from typing import Any, TYPE_CHECKING

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.Items, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.Items:
    behavior_packs:DataMinerTyping.BehaviorPacks = dataminers["behavior_packs"].get_data_file(version, non_exist_ok=True)
    if behavior_packs is None:
        behavior_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    return {item_name: CollapseResourcePacks.collapse_resource_packs(item_behavior_packs, behavior_packs, version.name) for item_name, item_behavior_packs in data.items()}

def behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

comparer = ComparerImporter.load_from_file("items", {
    "normalize": normalize,
    "behavior_pack_comparison_move_function": behavior_pack_comparison_move_function,
})
