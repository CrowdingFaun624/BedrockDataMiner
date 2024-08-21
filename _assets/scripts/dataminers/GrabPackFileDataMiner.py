from typing import Any, Literal

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import DataMiner.DataTypes as DataTypes
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["GrabPackFileDataMiner"]

class GrabPackFileDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
    )

    @classmethod
    def manipulate_arguments(cls, arguments: dict[str, Any]) -> None:
        if "data_type" in arguments:
            arguments["data_type"] = DataTypes.DataTypes[arguments["data_type"]]

    def initialize(self, locations:list[str], pack_type:Literal["resource_packs", "behavior_packs"], data_type:DataTypes.DataTypes=DataTypes.DataTypes.json) -> None:
        self.locations = locations
        self.pack_type = pack_type
        self.data_type = data_type

    def get_packs(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.ResourcePacks:
        return environment.dependency_data.get(self.pack_type, self)

    def get_files(self, packs:DataMinerTyping.ResourcePacks, accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> tuple[dict[str,Any], dict[str,str]]:
        '''
        Returns a dictionary of file names to file contents and a dictionary of file names to the pack they belong to.
        '''
        pack_files:dict[str,str] = {}
        for location in self.locations:
            pack_files.update((pack["path"] + location, pack["name"]) for pack in packs)
        files_request = DataTypes.get_file_request(pack_files.keys(), self.data_type)
        files:dict[str,Any] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return files, pack_files

    def get_output(self, files:dict[str,Any], pack_files:dict[str,str], environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,Any]:
        return {pack_files[pack_file]: data for pack_file, data in files.items()}

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        packs = self.get_packs(environment)
        files, pack_files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, pack_files, environment)
        return Sorting.sort_everything(output)
