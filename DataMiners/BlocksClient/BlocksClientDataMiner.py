import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class BlocksClientDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> dict[str,dict[str,DataMinerTyping.BlocksJsonClientBlockTypedDict]]:
        return super().activate(dependency_data)
