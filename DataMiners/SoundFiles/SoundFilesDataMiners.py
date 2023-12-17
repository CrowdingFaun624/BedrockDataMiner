import DataMiners.DataMiner as DataMiner
import DataMiners.SoundFiles.SoundFilesDataMiner0 as SoundFilesDataMiner0

dataminers = DataMiner.DataMinerCollection("sound_files.json", "sound_files", [
    DataMiner.DataMinerSettings("-", "-", SoundFilesDataMiner0.SoundFilesDataMiner0, [])
])
