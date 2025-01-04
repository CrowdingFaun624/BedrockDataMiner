import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Downloader.DirectoryAccessor as DirectoryAccessor
import Utilities.FileManager as FileManager


class AllFilesDataminer(Dataminer.Dataminer):

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> dict[str,str]:
        accessor = self.get_accessor(DirectoryAccessor.DirectoryAccessor)
        return {file: FileManager.get_hash_hexdigest(accessor.read(file)) for file in accessor.file_list}
