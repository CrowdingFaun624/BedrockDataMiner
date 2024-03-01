import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class LanguagesDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.LanguagesTypedDict]:
        return super().activate(dependency_data)
