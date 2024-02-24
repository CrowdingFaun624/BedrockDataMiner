import DataMiners.SoundFiles.SoundFilesDataMiner0 as SoundFilesDataMiner0

# dataminers = DataMiner.DataMinerCollection("sound_files.json", "sound_files", SoundFilesComparer.comparer, [
#     DataMiner.DataMinerSettings("-", "-", SoundFilesDataMiner0.SoundFilesDataMiner0, [])
# ])

dataminers = [
    SoundFilesDataMiner0.SoundFilesDataMiner0,
]
