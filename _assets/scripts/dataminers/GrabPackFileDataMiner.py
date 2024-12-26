from itertools import product
from typing import Any, Literal

import _assets.scripts.dataminers.PacksDataMiner as PacksDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["GrabPackFileDataMiner"]

class GrabPackFileDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs", "skin_packs", "emotes", "pieces"))),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_packs", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_file_name", "a str", False, str),
    )

    def initialize(self, location:str|list[str], pack_type:Literal["resource_packs", "behavior_packs", "skin_packs", "emotes", "pieces"], find_none_okay:bool=False, ignore_packs:list[str]|None=None, insert_file_name:str|None=None) -> None:
        self.location = [location] if isinstance(location, str) else location
        self.pack_type = pack_type
        self.find_none_okay = find_none_okay
        self.ignore_packs:set[str] = set(ignore_packs) if ignore_packs is not None else set()
        self.insert_file_name = insert_file_name

    def get_coverage(self, file_set:FileDataMiner.FileSet, environment: DataMinerEnvironment.DataMinerEnvironment) -> set[str]:
        packs = [pack["path"] for pack in self.get_packs(environment) if pack["name"] not in self.ignore_packs]
        output:set[str] = set()
        for pack, location in product(packs, self.location):
            file_name = pack + location
            if file_set.file_exists(file_name):
                output.add(file_name)
        if len(output) == 0 and not self.find_none_okay:
            raise Exceptions.DataMinerNothingFoundError(self)
        return output

    def get_packs(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[PacksDataMiner.PackTypedDict]:
        return environment.dependency_data.get(self.pack_type, self)

    def get_files(self, packs:list[PacksDataMiner.PackTypedDict], accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[tuple[str,str],bytes]:
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
            raise Exceptions.DataMinerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str],bytes], environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,File.File|Any]:
        if self.insert_file_name is None:
            return {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}
        else:
            return {self.insert_file_name: {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}}

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        packs = self.get_packs(environment)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return Sorting.sort_everything(output)
