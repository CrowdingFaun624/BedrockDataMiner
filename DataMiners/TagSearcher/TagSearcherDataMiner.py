import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Structure.DataPath as DataPath

class TagSearcherDataMiner(DataMiner.DataMiner):
    
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> list[DataPath.DataPath]:
        return super().activate(dependency_data)
