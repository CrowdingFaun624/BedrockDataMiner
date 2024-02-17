import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.MyMusicDefinitions, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.MyMusicDefinitions:
    resource_packs:DataMinerTyping.ResourcePacks = dependencies["resource_packs"]
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    return {environment_name: CollapseResourcePacks.collapse_resource_packs(environment_properties, resource_packs) for environment_name, environment_properties in data.items()}

comparer = ComparerImporter.load_from_file("music_definitions", {"normalize": normalize})
