import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class ModelsDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Models:
        return super().activate(dependency_data)
