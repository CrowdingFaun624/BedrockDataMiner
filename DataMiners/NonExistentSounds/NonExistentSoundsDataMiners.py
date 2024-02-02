
import DataMiners.DataMiner as DataMiner
import DataMiners.NonExistentSounds.NonExistentSoundsComparer as NonExistentSoundsComparer
import DataMiners.NonExistentSounds.NonExistentSoundsDataMiner0 as NonExistentSoundsDataMiner0

dataminers = DataMiner.DataMinerCollection("non_existent_sounds.json", "non_existent_sounds", NonExistentSoundsComparer.comparer, [
    DataMiner.DataMinerSettings("1.0.4.1", "-", NonExistentSoundsDataMiner0.NonExistentSoundsDataMiner0, ["sound_definitions", "sound_files", "resource_packs"], resource_packs_location="resource_packs"),
    DataMiner.DataMinerSettings("a0.11.2", "1.0.4.1", NonExistentSoundsDataMiner0.NonExistentSoundsDataMiner0, ["sound_definitions", "sound_files", "resource_packs"], resource_packs_location=None), # sounds are not in resource packs
    # before a0.11.2, sound_definitions.json no longer exists.
])
