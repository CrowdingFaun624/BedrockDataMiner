import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class DuplicateSoundsDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> dict[str,DataMinerTyping.DuplicateSoundsTypedDict]:
        return super().activate(dependency_data)
