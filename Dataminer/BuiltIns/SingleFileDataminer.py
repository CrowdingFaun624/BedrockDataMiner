from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import FileDataminer, FileSet
from Downloader.FileAccessor import FileAccessor
from Utilities.File import File
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class SingleFileDataminer(FileDataminer):

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("file_name", True, str),
    )

    def initialize(self, file_name:str) -> None:
        self.file_name = file_name

    def get_coverage(self, file_set: FileSet, environment: DataminerEnvironment) -> set[str]:
        return {self.file_name}

    def activate(self, environment: DataminerEnvironment) -> File:
        return self.export_file(self.get_accessor(FileAccessor).read(), self.file_name)
