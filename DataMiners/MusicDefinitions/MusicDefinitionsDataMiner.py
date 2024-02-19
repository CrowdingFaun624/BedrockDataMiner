import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class MusicDefinitionsDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.MyMusicDefinitions:
        return super().activate(dependency_data)
