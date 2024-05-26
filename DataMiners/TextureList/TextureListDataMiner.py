import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerEnvironment as DataMinerEnvironment


class TextureListDataMiner(DataMiner.DataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,list[str]]:
        return super().activate(environment)
