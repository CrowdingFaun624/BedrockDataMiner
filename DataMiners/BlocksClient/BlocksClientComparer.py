import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.MyBlocksClient, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedBlocksClient:
    def fix_properties(properties:DataMinerTyping.MyBlocksJsonClientBlockTypedDict) -> DataMinerTyping.MyBlocksJsonClientBlockTypedDict:
        for resource_pack_name, resource_pack_properties in properties.items():
            if "sounds" in resource_pack_properties: del resource_pack_properties["sounds"] # MCPE-76182
        return properties
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dependencies["resource_packs"]
    output = {datum["name"]: CollapseResourcePacks.collapse_resource_packs(fix_properties(datum["properties"]), resource_packs) for datum in data}
    return output

def resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

comparer = ComparerImporter.load_from_file("blocks_client", {"normalize": normalize, "resource_pack_comparison_move_function": resource_pack_comparison_move_function})
