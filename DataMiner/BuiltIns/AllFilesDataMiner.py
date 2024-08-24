import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Downloader.Accessor as Accessor


class AllFilesDataMiner(DataMiner.DataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[str]:
        return self.get_accessor("client", Accessor.DirectoryAccessor).get_file_list()
