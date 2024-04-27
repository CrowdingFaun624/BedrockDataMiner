import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.ResourcePacks.ResourcePacksDataMiner as ResourcePackDataMiner
from Utilities.FunctionCaller import FunctionCaller

behavior_pack_order = ResourcePackDataMiner.resource_pack_order

class BehaviorPacksDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.ResourcePackTypedDict]:
        return super().activate(dependency_data)
