import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment


class AllFilesDataMiner(DataMiner.DataMiner):
    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[str]:
        return super().activate(environment)
