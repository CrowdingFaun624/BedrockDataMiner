from typing import Any

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataTypes as DataTypes
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabSingleFileDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    @classmethod
    def manipulate_arguments(cls, arguments: dict[str, Any]) -> None:
        if "data_type" in arguments:
            arguments["data_type"] = DataTypes.DataTypes[arguments["data_type"]]

    def initialize(self, locations:str|list[str], data_type:DataTypes.DataTypes=DataTypes.DataTypes.json, insert_pack:str|None=None) -> None:
        self.locations = [locations] if isinstance(locations, str) else locations
        self.data_type = data_type
        self.insert_pack = insert_pack

    def get_file(self, accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        for location in self.locations:
            if not accessor.file_exists(location):
                continue
            return DataTypes.get_data(self, location, self.data_type, accessor)
        else:
            raise Exceptions.DataMinerNothingFoundError(self)

    def get_output(self, file:Any, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        return file

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        file = self.get_file(accessor, environment)
        file_data = self.get_output(file, environment)
        return Sorting.sort_everything(file_data)
