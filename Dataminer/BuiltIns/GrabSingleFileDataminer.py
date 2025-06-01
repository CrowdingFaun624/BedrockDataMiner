from typing import Any

import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Downloader.DirectoryAccessor as DirectoryAccessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier


class GrabSingleFileDataminer(FileDataminer.FileDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", True, str),
    )

    def initialize(self, location:str) -> None:
        self.location = location

    def get_coverage(self, file_set:FileDataminer.FileSet, environment:DataminerEnvironment.DataminerEnvironment) -> set[str]:
        if file_set.file_exists(self.location):
            return {self.location}
        else:
            raise Exceptions.DataminerNothingFoundError(self)

    def get_file(self, accessor:DirectoryAccessor.DirectoryAccessor, environment:DataminerEnvironment.DataminerEnvironment) -> tuple[bytes, str]:
        if not accessor.file_exists(self.location):
            raise Exceptions.DataminerNothingFoundError(self)
        return accessor.read(self.location), self.location

    def get_output(self, file:bytes, file_name:str, environment:DataminerEnvironment.DataminerEnvironment) -> File.File:
        return self.export_file(file, file_name)

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor.DirectoryAccessor)
        file, file_name = self.get_file(accessor, environment)
        file_data = self.get_output(file, file_name, environment)
        return file_data
