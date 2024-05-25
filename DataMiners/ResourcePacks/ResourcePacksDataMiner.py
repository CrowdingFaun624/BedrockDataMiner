import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping


class ResourcePacksDataMiner(DataMiner.DataMiner):
    
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.ResourcePackTypedDict]:
        return super().activate(dependency_data)
