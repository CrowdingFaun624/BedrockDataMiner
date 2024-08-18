from typing import Any

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataTypes as DataTypes
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabSingleFileDataMiner(DataMiner.DataMiner):

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

    def get_file(self, accessor:Accessor.Accessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> bytes|str:
        for location in self.locations:
            if not accessor.file_exists(location):
                continue
            return self.get_accessor("client").read(location, self.data_type.get_data_format())
        else:
            raise Exceptions.DataMinerNothingFoundError(self)

    def get_output(self, file:bytes|str, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        return DataTypes.get_data_from_content(file, self.data_type)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client")
        file = self.get_file(accessor, environment)
        file_data = self.get_output(file, environment)
        return Sorting.sort_everything(file_data)
