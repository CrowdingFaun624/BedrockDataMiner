import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class AllFilesDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> list[str]:
        return super().activate(dependency_data)
