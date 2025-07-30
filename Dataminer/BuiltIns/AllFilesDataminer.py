from Component.ComponentFunctions import register_builtin
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.FileManager import get_hash_hexdigest


@register_builtin()
class AllFilesDataminer(Dataminer):

    __slots__ = ()

    def activate(self, environment:DataminerEnvironment) -> dict[str,str]:
        accessor = self.get_accessor(DirectoryAccessor)
        return {file: get_hash_hexdigest(accessor.read(file)) for file in accessor.file_list}
