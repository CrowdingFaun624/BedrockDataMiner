from typing import Any

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabSingleFileDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def initialize(self, locations:list[str]) -> None:
        self.locations = locations

    def get_coverage(self, file_set: set[str], environment:DataMinerEnvironment.DataMinerEnvironment) -> set[str]:
        for file_name in self.locations:
            if file_name in file_set:
                return {file_name}
        else:
            return set()

    def get_file(self, accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> tuple[bytes, str]:
        for location in self.locations:
            if not accessor.file_exists(location):
                continue
            return accessor.read(location, "b"), location
        else:
            raise Exceptions.DataMinerNothingFoundError(self)

    def get_output(self, file:bytes, file_name:str, environment:DataMinerEnvironment.DataMinerEnvironment) -> File.File|Any:
        return self.export_file(file, file_name)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        file, file_name = self.get_file(accessor, environment)
        file_data = self.get_output(file, file_name, environment)
        return Sorting.sort_everything(file_data)
