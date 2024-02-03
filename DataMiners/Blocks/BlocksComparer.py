from typing import TYPE_CHECKING

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MyBlocks, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedBlocks:
    def fix_properties(properties:DataMinerTyping.MyBlocksJsonBlockTypedDict) -> DataMinerTyping.MyBlocksJsonBlockTypedDict:
        for resource_pack_name, resource_pack_properties in properties.items():
            if "sounds" in resource_pack_properties: del resource_pack_properties["sounds"] # MCPE-76182
        return properties
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dataminers["resource_packs"].get_data_file(version, True)
    output = {datum["name"]: CollapseResourcePacks.collapse_resource_packs(fix_properties(datum["properties"]), resource_packs, version.name) for datum in data}
    return output

def resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

comparer = ComparerImporter.load_from_file("blocks", {"normalize": normalize, "resource_pack_comparison_move_function": resource_pack_comparison_move_function})
