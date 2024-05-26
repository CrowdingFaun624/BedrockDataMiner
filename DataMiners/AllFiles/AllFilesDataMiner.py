import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerEnvironment as DataMinerEnvironment


class AllFilesDataMiner(DataMiner.DataMiner):
    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[str]:
        return super().activate(environment)
