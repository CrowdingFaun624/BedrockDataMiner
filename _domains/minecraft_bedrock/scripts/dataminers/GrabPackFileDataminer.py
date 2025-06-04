from itertools import product
from typing import Any, Literal, Sequence

import _domains.minecraft_bedrock.scripts.dataminers.PacksDataminer as PacksDataminer
import Downloader.DirectoryAccessor as DirectoryAccessor
import Utilities.Exceptions as Exceptions
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import FileDataminer, FileSet
from Utilities.File import File
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)

__all__ = ("GrabPackFileDataminer",)

class GrabPackFileDataminer(FileDataminer):

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("location", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("pack_type", True, EnumTypeVerifier(("resource_packs", "behavior_packs", "skin_packs", "emotes", "pieces"))),
        TypedDictKeyTypeVerifier("ignore_packs", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("find_none_okay", False, bool),
        TypedDictKeyTypeVerifier("insert_file_name", False, str),
    )

    def initialize(self, location:str|Sequence[str], pack_type:Literal["resource_packs", "behavior_packs", "skin_packs", "emotes", "pieces"], find_none_okay:bool=False, ignore_packs:list[str]|None=None, insert_file_name:str|None=None) -> None:
        self.location = (location,) if isinstance(location, str) else location
        self.pack_type = pack_type
        self.find_none_okay = find_none_okay
        self.ignore_packs:set[str] = set(ignore_packs) if ignore_packs is not None else set()
        self.insert_file_name = insert_file_name

    def get_coverage(self, file_set:FileSet, environment: DataminerEnvironment) -> set[str]:
        packs = (pack["path"] for pack in self.get_packs(environment) if pack["name"] not in self.ignore_packs)
        output:set[str] = set()
        for pack, location in product(packs, self.location):
            file_name = pack + location
            if file_set.file_exists(file_name):
                output.add(file_name)
        if len(output) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return output

    def get_packs(self, environment:DataminerEnvironment) -> list[PacksDataminer.PackTypedDict]:
        return environment.dependency_data.get(self.pack_type, self)

    def get_files(self, packs:list[PacksDataminer.PackTypedDict], accessor:DirectoryAccessor.DirectoryAccessor, environment:DataminerEnvironment) -> dict[tuple[str,str],bytes]:
        '''
        Returns a dictionary of the pack the the files are in and the file's name to the file's contents.
        '''
        files:dict[tuple[str,str], bytes] = {}
        for pack, location in product(packs, self.location):
            if pack["name"] in self.ignore_packs:
                continue
            path = pack["path"] + location
            if accessor.file_exists(path):
                files[pack["name"], path] = accessor.read(path)
        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str],bytes], environment:DataminerEnvironment) -> dict[str,File|Any]:
        if self.insert_file_name is None:
            return {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}
        else:
            return {self.insert_file_name: {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}}

    def activate(self, environment:DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor.DirectoryAccessor)
        packs = self.get_packs(environment)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return output
