import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Downloader.Accessor as Accessor
import Utilities.FileManager as FileManager


class AllFilesDataminer(Dataminer.Dataminer):

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> dict[str,str]:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        return {file: FileManager.get_hash_hexdigest(accessor.read(file)) for file in accessor.get_file_list()}
