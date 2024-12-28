from typing import Any

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabSingleFileDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, location:str) -> None:
        self.location = location

    def get_coverage(self, file_set:FileDataMiner.FileSet, environment:DataMinerEnvironment.DataMinerEnvironment) -> set[str]:
        if file_set.file_exists(self.location):
            return {self.location}
        else:
            raise Exceptions.DataMinerNothingFoundError(self)

    def get_file(self, accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> tuple[bytes, str]:
        if not accessor.file_exists(self.location):
            raise Exceptions.DataMinerNothingFoundError(self)
        return accessor.read(self.location), self.location

    def get_output(self, file:bytes, file_name:str, environment:DataMinerEnvironment.DataMinerEnvironment) -> File.File|Any:
        return self.export_file(file, file_name)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        file, file_name = self.get_file(accessor, environment)
        file_data = self.get_output(file, file_name, environment)
        return file_data
