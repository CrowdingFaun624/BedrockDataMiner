import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Downloader.Accessor as Accessor
import Utilities.FileManager as FileManager


class AllFilesDataMiner(DataMiner.DataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,str]:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        return {file: FileManager.get_hash_hexdigest(accessor.read(file)) for file in accessor.get_file_list()}
