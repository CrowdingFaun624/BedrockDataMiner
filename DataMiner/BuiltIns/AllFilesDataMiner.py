import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor


class AllFilesDataMiner(FileDataMiner.FileDataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[str]:
        return self.get_accessor("client", Accessor.DirectoryAccessor).get_file_list()
