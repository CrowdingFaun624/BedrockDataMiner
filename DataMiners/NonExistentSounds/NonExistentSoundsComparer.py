from typing import TYPE_CHECKING

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.NonExistentSounds, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedNonExistentSounds:
    resource_packs = dataminers["resource_packs"].get_data_file(version, non_exist_ok=True)
    if resource_packs is None: resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    return {sound_event_name: CollapseResourcePacks.collapse_resource_packs(sound_event_properties, resource_packs, version.name, False) for sound_event_name, sound_event_properties in data.items()}

comparer = ComparerImporter.load_from_file("non_existent_sounds", {"normalize": normalize})

