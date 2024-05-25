import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.ResourcePacks.ResourcePacksDataMiner as ResourcePackDataMiner

class BehaviorPacksDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.ResourcePackTypedDict]:
        return super().activate(dependency_data)
