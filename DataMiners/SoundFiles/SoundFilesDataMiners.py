import DataMiners.DataMiner as DataMiner
import DataMiners.SoundFiles.SoundFilesComparer as SoundFilesComparer
import DataMiners.SoundFiles.SoundFilesDataMiner0 as SoundFilesDataMiner0

dataminers = DataMiner.DataMinerCollection("sound_files.json", "sound_files", SoundFilesComparer.comparer, [
    DataMiner.DataMinerSettings("-", "-", SoundFilesDataMiner0.SoundFilesDataMiner0, [])
])
