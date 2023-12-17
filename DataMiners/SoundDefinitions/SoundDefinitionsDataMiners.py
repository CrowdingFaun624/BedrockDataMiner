import DataMiners.DataMiner as DataMiner
import DataMiners.SoundDefinitions.SoundDefinitionsDataMiner0 as SoundDefinitionsDataMiner0

dataminers = DataMiner.DataMinerCollection("sound_definitions.json", "sound_definitions", [
    DataMiner.DataMinerSettings("-", "-", SoundDefinitionsDataMiner0.SoundDefinitionsDataMiner0, ["resource_packs"])
])