import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class RecipesDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Recipes:
        return super().activate(dependency_data)
