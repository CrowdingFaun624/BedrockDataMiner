import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.NonExistentSounds, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedNonExistentSounds:
    resource_packs = dependencies["resource_packs"]
    if resource_packs is None: resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    return {sound_event_name: CollapseResourcePacks.collapse_resource_packs(sound_event_properties, resource_packs, False) for sound_event_name, sound_event_properties in data.items()}

comparer = ComparerImporter.load_from_file("non_existent_sounds", {"normalize": normalize})

