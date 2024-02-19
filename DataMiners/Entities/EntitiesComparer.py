from typing import Any

import Comparison.ComparerImporter as ComparerImporter
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

def behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def fix_out_of_bounds_components(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for key_to_delete in [key for key in data if key.startswith("minecraft:")]:
        del data[key_to_delete]

def fix_MCPE_178417(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-178417
    for key_to_delete in [key for key in data if key.startswith("minecraft:")]:
        del data[key_to_delete]

comparer = ComparerImporter.load_from_file("entities", {
    "behavior_pack_comparison_move_function": behavior_pack_comparison_move_function,
    "collapse_resource_packs": CollapseResourcePacks.make_interface(pack_key="behavior_packs"),
    "fix_MCPE_178417": fix_MCPE_178417,
    "fix_out_of_bounds_components": fix_out_of_bounds_components,
})
