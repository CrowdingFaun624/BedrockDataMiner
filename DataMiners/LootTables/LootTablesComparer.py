from typing import Any

import Comparison.ComparerImporter as ComparerImporter
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import DataMiners.DataMinerTyping as DataMinerTyping

def behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def normalize_conditions(data:dict[str,list[dict[str,Any]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "conditions" not in data: return
    output:dict[str[dict[str,Any]]] = {}
    for condition in data["conditions"]:
        condition_name = condition["condition"]
        output[condition_name] = condition
        del condition["condition"]
    data["conditions"] = output

def normalize_functions(data:dict[str,list[dict[str,Any]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "functions" not in data: return
    output:dict[str,dict[str,Any]] = {}
    for function in data["functions"]:
        function_name = function["function"]
        output[function_name] = function
        del function["function"]
    data["functions"] = output

comparer = ComparerImporter.load_from_file("loot_tables", {
    "behavior_pack_comparison_move_function": behavior_pack_comparison_move_function,
    "collapse_resource_packs": CollapseResourcePacks.make_interface(pack_key="behavior_packs"),
    "normalize_conditions": normalize_conditions,
    "normalize_functions": normalize_functions,
})
