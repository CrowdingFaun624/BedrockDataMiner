from itertools import product
from typing import Any, Sequence

from _domains.minecraft_java.scripts.dataminers.PacksDataminer import PackTypedDict
from Component.ComponentFunctions import component_function
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import FileDataminer, FileSet
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.Exceptions import DataminerNothingFoundError
from Utilities.File import File
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


@component_function()
class GrabPackFileDataminer(FileDataminer):

    __slots__ = (
        "find_none_okay",
        "insert_file_name",
        "location",
        "pack_or_namespace",
        "pack_type",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("location", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("pack_type", True, str),
        TypedDictKeyTypeVerifier("is_namespace", False, bool),
        TypedDictKeyTypeVerifier("find_none_okay", False, bool),
        TypedDictKeyTypeVerifier("insert_file_name", False, str),
    )

    def initialize(self, location:str|Sequence[str], pack_type:str, is_namespace:bool=True, find_none_okay:bool=False, insert_file_name:str|None=None) -> None:
        self.location = (location,) if isinstance(location, str) else location
        self.pack_type = pack_type
        self.pack_or_namespace = ["packs", "namespaces"][is_namespace]
        self.find_none_okay = find_none_okay
        self.insert_file_name = insert_file_name

    def get_coverage(self, file_set:FileSet, environment: DataminerEnvironment) -> set[str]:
        packs = list(self.get_packs(environment).keys())
        output:set[str] = set()
        for pack, location in product(packs, self.location):
            file_name = pack + location
            if file_set.file_exists(file_name):
                output.add(file_name)
        if len(output) == 0 and not self.find_none_okay:
            raise DataminerNothingFoundError(self)
        return output

    def get_packs(self, environment:DataminerEnvironment) -> dict[str,PackTypedDict]:
        return environment.dependency_data.get(self.pack_type, self)[self.pack_or_namespace]

    def get_files(self, packs:dict[str,PackTypedDict], accessor:DirectoryAccessor, environment:DataminerEnvironment) -> dict[tuple[str,str],bytes]:
        '''
        Returns a dictionary of the pack the the files are in and the file's name to the file's contents.
        '''
        pack_path_name = [(pack_path, pack["name"]) for pack_path, pack in packs.items()]
        files:dict[tuple[str,str], bytes] = {}
        for (pack_path, pack_name), location in product(pack_path_name, self.location):
            path = pack_path + location
            if accessor.file_exists(path):
                files[pack_name, path] = accessor.read(path)
        if len(files) == 0 and not self.find_none_okay:
            raise DataminerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str],bytes], environment:DataminerEnvironment) -> dict[str,File|Any]:
        if self.insert_file_name is None:
            return {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}
        else:
            return {self.insert_file_name: {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}}

    def activate(self, environment:DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor)
        packs = self.get_packs(environment)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return output
