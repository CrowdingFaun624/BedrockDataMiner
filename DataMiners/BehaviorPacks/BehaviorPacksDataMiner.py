import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.ResourcePacks.ResourcePacksDataMiner as ResourcePackDataMiner
from Utilities.FunctionCaller import FunctionCaller

get_behavior_pack_order = FunctionCaller(ResourcePackDataMiner.get_resource_pack_order, ["behavior pack"])

class BehaviorPacksDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.ResourcePackTypedDict]:
        return super().activate()
