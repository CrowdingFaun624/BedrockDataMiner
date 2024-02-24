import DataMiners.MusicDefinitions.MusicDefinitionsDataMiner0 as MusicDefinitionsDataMiner0

# dataminers = DataMiner.DataMinerCollection("music_definitions.json", "music_definitions", MusicDefinitionsComparer.comparer, [
#     DataMiner.DataMinerSettings("-", "-", MusicDefinitionsDataMiner0.MusicDefinitionsDataMiner0, ["resource_packs"]),
# ])

dataminers = [
    MusicDefinitionsDataMiner0.MusicDefinitionsDataMiner0,
]
