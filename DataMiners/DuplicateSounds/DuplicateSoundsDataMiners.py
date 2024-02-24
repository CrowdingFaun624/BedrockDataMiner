import DataMiners.DuplicateSounds.DuplicateSoundsDataMiner0 as DuplicateSoundsDataMiner0

# dataminers = DataMiner.DataMinerCollection("duplicate_sounds.json", "duplicate_sounds", DuplicateSoundsComparer.comparer, [
#     DataMiner.DataMinerSettings("-", "-", DuplicateSoundsDataMiner0.DuplicateSoundsDataMiner0, ["sound_files"])
# ])

dataminers = [
    DuplicateSoundsDataMiner0.DuplicateSoundsDataMiner0,
]
