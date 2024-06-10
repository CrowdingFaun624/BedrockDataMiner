import DataMiner.AllFiles.AllFilesDataMiner as AllFilesDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment


class AllFilesDataMiner0(AllFilesDataMiner.AllFilesDataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[str]:
        return self.get_accessor("client").get_file_list()
