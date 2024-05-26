import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping


class ResourcePacksDataMiner(DataMiner.DataMiner):
    
    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.ResourcePackTypedDict]:
        return super().activate(environment)
