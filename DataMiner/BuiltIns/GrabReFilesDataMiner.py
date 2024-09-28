import re

import DataMiner.BuiltIns.GrabMultipleFilesDataMiner as GrabMultipleFilesDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabReFilesDataMiner(GrabMultipleFilesDataMiner.GrabMultipleFilesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("directory", "a str", True, str, function=FileDataMiner.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("pattern", "a str", True, str)
    )

    def initialize(self, directory:str, pattern:str) -> None:
        self.directory = directory
        self.pattern = re.compile(pattern)

    def get_coverage(self, file_set: set[str], environment:DataMinerEnvironment.DataMinerEnvironment) -> set[str]:
        start_index = len(self.directory)
        output = {
            file_name
            for file_name in file_set
            if file_name.startswith(self.directory) and self.pattern.fullmatch(file_name, start_index)
        }
        if len(output) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return output

    def get_files(self, accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[tuple[str,str],bytes]:
        output:dict[tuple[str,str],bytes] = {}
        for file_name in accessor.get_files_in(self.directory):
            if self.pattern.fullmatch(file_name, len(self.directory)):
                relative_name = file_name.removeprefix(self.directory)
                output[relative_name, file_name] = accessor.read(file_name, "b")
        if len(output) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return output
