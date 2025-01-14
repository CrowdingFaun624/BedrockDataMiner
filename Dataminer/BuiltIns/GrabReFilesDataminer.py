import re
from typing import Any

import Dataminer.BuiltIns.GrabMultipleFilesDataminer as GrabMultipleFilesDataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Downloader.DirectoryAccessor as DirectoryAccessor
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier


class GrabReFilesDataminer(GrabMultipleFilesDataminer.GrabMultipleFilesDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("directory", True, str, function=FileDataminer.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("pattern", True, str)
    )

    def initialize(self, directory:str, pattern:str) -> None:
        self.directory = directory
        self.pattern = re.compile(pattern)

    def get_coverage(self, file_set:FileDataminer.FileSet, environment:DataminerEnvironment.DataminerEnvironment) -> set[str]:
        start_index = len(self.directory)
        output = {
            file_name
            for file_name in file_set.get_files_in(self.directory)
            if self.pattern.fullmatch(file_name, start_index)
        }
        if len(output) == 0:
            raise Exceptions.DataminerNothingFoundError(self)
        return output

    def get_files(self, accessor:DirectoryAccessor.DirectoryAccessor, environment:DataminerEnvironment.DataminerEnvironment) -> dict[tuple[str,str],bytes]:
        output:dict[tuple[str,str],bytes] = {}
        for file_name in accessor.get_files_in(self.directory):
            if self.pattern.fullmatch(file_name, len(self.directory)):
                relative_name = file_name.removeprefix(self.directory)
                output[relative_name, file_name] = accessor.read(file_name)
        if len(output) == 0:
            raise Exceptions.DataminerNothingFoundError(self)
        return output

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor.DirectoryAccessor)
        files = self.get_files(accessor, environment)
        output = self.get_output(files, accessor, environment)
        return output
