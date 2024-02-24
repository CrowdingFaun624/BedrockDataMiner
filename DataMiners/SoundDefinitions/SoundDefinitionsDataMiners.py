import DataMiners.SoundDefinitions.SoundDefinitionsDataMiner0 as SoundDefinitionsDataMiner0
import DataMiners.SoundDefinitions.SoundDefinitionsDataMiner1 as SoundDefinitionsDataMiner1

# dataminers = DataMiner.DataMinerCollection("sound_definitions.json", "sound_definitions", SoundDefinitionsComparer.comparer, [
#     DataMiner.DataMinerSettings("1.0.4", "-", SoundDefinitionsDataMiner0.SoundDefinitionsDataMiner0, ["resource_packs"]),
#     DataMiner.DataMinerSettings("a0.11.2", "1.0.4", SoundDefinitionsDataMiner1.SoundDefinitionsDataMiner1, []),
#     # Prior to a0.12.1_build1 (surrounding versions are unarchived), no files about sounds exist.
# ])

dataminers = [
    SoundDefinitionsDataMiner0.SoundDefinitionsDataMiner0,
    SoundDefinitionsDataMiner1.SoundDefinitionsDataMiner1,
]
