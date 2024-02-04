from typing import TYPE_CHECKING

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MyMusicDefinitions, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.MyMusicDefinitions:
    resource_packs:DataMinerTyping.ResourcePacks = dataminers["resource_packs"].get_data_file(version, non_exist_ok=True)
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    return {environment_name: CollapseResourcePacks.collapse_resource_packs(environment_properties, resource_packs, version.name) for environment_name, environment_properties in data.items()}

comparer = ComparerImporter.load_from_file("music_definitions", {"normalize": normalize})
