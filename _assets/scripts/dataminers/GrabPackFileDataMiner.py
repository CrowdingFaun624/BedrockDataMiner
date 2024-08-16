from typing import Any, Literal

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.DataTypes as DataTypes
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["GrabPackFileDataMiner"]

class GrabPackFileDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
    )

    def initialize(self, **kwargs) -> None:
        self.data_type = DataTypes.DataTypes[kwargs.get("data_type", "json")]
        self.locations:list[str] = kwargs["locations"]
        self.pack_type:Literal["resource_packs", "behavior_packs"] = kwargs["pack_type"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        packs:DataMinerTyping.ResourcePacks|DataMinerTyping.BehaviorPacks = environment.dependency_data.get(self.pack_type, self)
        pack_names = [(pack["name"], pack["path"]) for pack in packs]
        pack_files:dict[str,str] = {}
        for blocks_location in self.locations:
            pack_files.update({pack_path + blocks_location: pack_name for pack_name, pack_path in pack_names})
        files_request = DataTypes.get_file_request(pack_files.keys(), self.data_type)
        accessor = self.get_accessor("client")
        files:dict[str,Any] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output = {pack_files[pack_file]: data for pack_file, data in files.items()}
        return Sorting.sort_everything(output)
