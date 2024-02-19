from typing import Any

import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

def behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

comparer = ComparerImporter.load_from_file("items", {
    "collapse_resource_packs": CollapseResourcePacks.make_interface(pack_key="behavior_packs"),
    "behavior_pack_comparison_move_function": behavior_pack_comparison_move_function,
})
