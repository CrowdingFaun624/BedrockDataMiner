import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class SoundsJsonDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.MySoundsJsonTypedDict:
        return super().activate(dependency_data)