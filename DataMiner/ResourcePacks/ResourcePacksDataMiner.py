import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping


class ResourcePacksDataMiner(DataMiner.DataMiner):
    
    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.ResourcePackTypedDict]:
        return super().activate(environment)
