from itertools import product
from typing import Any

import _domains.minecraft_java.scripts.dataminers.PacksDataminer as PacksDataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Downloader.DirectoryAccessor as DirectoryAccessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["GrabPackFileDataminer"]

class GrabPackFileDataminer(FileDataminer.FileDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_file_name", "a str", False, str),
    )

    def initialize(self, location:str|list[str], pack_type:str, find_none_okay:bool=False, insert_file_name:str|None=None) -> None:
        self.location = [location] if isinstance(location, str) else location
        self.pack_type = pack_type
        self.find_none_okay = find_none_okay
        self.insert_file_name = insert_file_name

    def get_coverage(self, file_set:FileDataminer.FileSet, environment: DataminerEnvironment.DataminerEnvironment) -> set[str]:
        packs = [pack["path"] for pack in self.get_packs(environment)]
        output:set[str] = set()
        for pack, location in product(packs, self.location):
            file_name = pack + location
            if file_set.file_exists(file_name):
                output.add(file_name)
        if len(output) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return output

    def get_packs(self, environment:DataminerEnvironment.DataminerEnvironment) -> list[PacksDataminer.PackTypedDict]:
        return environment.dependency_data.get(self.pack_type, self)

    def get_files(self, packs:list[PacksDataminer.PackTypedDict], accessor:DirectoryAccessor.DirectoryAccessor, environment:DataminerEnvironment.DataminerEnvironment) -> dict[tuple[str,str],bytes]:
        '''
        Returns a dictionary of the pack the the files are in and the file's name to the file's contents.
        '''
        files:dict[tuple[str,str], bytes] = {}
        for pack, location in product(packs, self.location):
            path = pack["path"] + location
            if accessor.file_exists(path):
                files[pack["name"], path] = accessor.read(path)
        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str],bytes], environment:DataminerEnvironment.DataminerEnvironment) -> dict[str,File.File|Any]:
        if self.insert_file_name is None:
            return {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}
        else:
            return {self.insert_file_name: {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}}

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor.DirectoryAccessor)
        packs = self.get_packs(environment)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return output
