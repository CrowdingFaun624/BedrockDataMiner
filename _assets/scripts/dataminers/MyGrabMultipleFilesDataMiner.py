from typing import Any

import DataMiner.BuiltIns.GrabMultipleFilesDataMiner as GrabMultipleFilesDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataTypes as DataTypes
import Downloader.Accessor as Accessor
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MyGrabMultipleFilesDataMiner"]

class MyGrabMultipleFilesDataMiner(GrabMultipleFilesDataMiner.GrabMultipleFilesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=GrabMultipleFilesDataMiner.location_function),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    def initialize(self, location:str, data_type:DataTypes.DataTypes=DataTypes.DataTypes.json, ignore_suffixes:list[str]|None=None, suffixes:list[str]|None=None, insert_pack:str|None=None) -> None:
        super().initialize(location, data_type, ignore_suffixes, suffixes)
        self.insert_pack = insert_pack

    def get_output(self, files: dict[str, str], accessor: Accessor.Accessor, environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str, dict[str, Any]]:
        output:dict[str,dict[str,Any]] = {}
        for file_name, path in files.items():
            file_data = DataTypes.get_data(self, path, self.data_type, accessor)
            if self.insert_pack is None:
                output[file_name] = file_data
            else:
                output[file_name] = {self.insert_pack: file_data}
        return output
