from typing import Any

from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import FileDataminer, FileSet
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.Exceptions import DataminerNothingFoundError
from Utilities.File import File
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class GrabSingleFileDataminer(FileDataminer):

    __slots__ = (
        "location",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("location", True, str),
    )

    def initialize(self, location:str) -> None:
        self.location = location

    def get_coverage(self, file_set:FileSet, environment:DataminerEnvironment) -> set[str]:
        if file_set.file_exists(self.location):
            return {self.location}
        else:
            raise DataminerNothingFoundError(self)

    def get_file(self, accessor:DirectoryAccessor, environment:DataminerEnvironment) -> tuple[bytes, str]:
        if not accessor.file_exists(self.location):
            raise DataminerNothingFoundError(self)
        return accessor.read(self.location), self.location

    def get_output(self, file:bytes, file_name:str, environment:DataminerEnvironment) -> File:
        return self.export_file(file, file_name)

    def activate(self, environment:DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor)
        file, file_name = self.get_file(accessor, environment)
        file_data = self.get_output(file, file_name, environment)
        return file_data
