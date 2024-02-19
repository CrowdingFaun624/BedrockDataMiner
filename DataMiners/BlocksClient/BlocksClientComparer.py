import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

def fix_MCPE_76182(data:DataMinerTyping.BlocksJsonClientBlockTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-76182
    if "sounds" in data:
        del data["sounds"]

def normalize(data:DataMinerTyping.MyBlocksClient, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedBlocksClient:
    return {block["name"]: block["properties"] for block in data}

def resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

comparer = ComparerImporter.load_from_file("blocks_client", {
    "collapse_resource_packs": CollapseResourcePacks.make_interface(),
    "fix_MCPE_76182": fix_MCPE_76182,
    "normalize": normalize,
    "resource_pack_comparison_move_function": resource_pack_comparison_move_function,
})
