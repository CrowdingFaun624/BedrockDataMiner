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
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
    )

    def initialize(self, locations:list[str], pack_type:Literal["resource_packs", "behavior_packs"], find_none_okay:bool=False) -> None:
        self.locations = locations
        self.pack_type = pack_type
        self.find_none_okay = find_none_okay

    def get_packs(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[PacksDataMiner.PackTypedDict]:
        return environment.dependency_data.get(self.pack_type, self)

    def get_files(self, packs:list[PacksDataMiner.PackTypedDict], accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[tuple[str,str],bytes]:
        '''
        Returns a dictionary of the pack the the files are in and the file's name to the file's contents.
        '''
        files:dict[tuple[str,str], bytes] = {}
        for pack in packs:
            for location in self.locations:
                path = pack["path"] + location
                if accessor.file_exists(path):
                    files[pack["name"], path] = accessor.read(path, "b")
                    break
                else:
                    continue
        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataMinerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str],bytes], environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,File.File|Any]:
        return {pack_name: self.export_file(file_content, file_name) for (pack_name, file_name), file_content in files.items()}

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        packs = self.get_packs(environment)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return Sorting.sort_everything(output)
