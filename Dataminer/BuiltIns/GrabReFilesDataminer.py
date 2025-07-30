import re
from typing import Any

import Dataminer.FileDataminer as FileDataminer
from Component.ComponentFunctions import register_builtin
from Dataminer.BuiltIns.GrabMultipleFilesDataminer import GrabMultipleFilesDataminer
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.Exceptions import DataminerNothingFoundError
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


@register_builtin()
class GrabReFilesDataminer(GrabMultipleFilesDataminer):

    __slots__ = (
        "directory",
        "pattern",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("directory", True, str, function=FileDataminer.location_value_function),
        TypedDictKeyTypeVerifier("pattern", True, str)
    )

    def initialize(self, directory:str, pattern:str) -> None:
        self.directory = directory
        self.pattern = re.compile(pattern)

    def get_coverage(self, file_set:FileDataminer.FileSet, environment:DataminerEnvironment) -> set[str]:
        start_index = len(self.directory)
        output = {
            file_name
            for file_name in file_set.get_files_in(self.directory)
            if self.pattern.fullmatch(file_name, start_index)
        }
        if len(output) == 0:
            raise DataminerNothingFoundError(self)
        return output

    def get_files(self, accessor:DirectoryAccessor, environment:DataminerEnvironment) -> dict[tuple[str,str],bytes]:
        output:dict[tuple[str,str],bytes] = {}
        for file_name in accessor.get_files_in(self.directory):
            if self.pattern.fullmatch(file_name, len(self.directory)):
                relative_name = file_name.removeprefix(self.directory)
                output[relative_name, file_name] = accessor.read(file_name)
        if len(output) == 0:
            raise DataminerNothingFoundError(self)
        return output

    def activate(self, environment:DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor)
        files = self.get_files(accessor, environment)
        output = self.get_output(files, accessor, environment)
        return output
