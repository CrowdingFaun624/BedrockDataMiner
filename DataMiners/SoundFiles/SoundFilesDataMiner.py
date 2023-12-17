import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

ALL_SOUND_FILE_FORMATS = [".fsb", ".ogg", ".wav", ".mpeg", ".mpg"]

class SoundFilesDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict|None=None) -> dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]]:
        return super().activate(dependency_data)