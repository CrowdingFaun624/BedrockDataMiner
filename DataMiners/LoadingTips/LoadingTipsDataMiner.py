import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class LoadingTipsDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.LoadingTips:
        return super().activate(dependency_data)
