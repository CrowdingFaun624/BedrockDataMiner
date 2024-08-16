from typing import Any

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataTypes as DataTypes
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabSingleFileDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    @classmethod
    def manipulate_arguments(cls, arguments: dict[str, Any]) -> None:
        if "data_type" in arguments:
            arguments["data_type"] = DataTypes.DataTypes[arguments["data_type"]]

    def initialize(self, location:str, data_type:DataTypes.DataTypes=DataTypes.DataTypes.json, insert_pack:str|None=None) -> None:
        self.location = location
        self.data_type = data_type
        self.insert_pack = insert_pack

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client")
        if not accessor.file_exists(self.location):
            raise Exceptions.DataMinerNothingFoundError(self)
        file = self.get_accessor("client").read(self.location, self.data_type.get_data_format())

        file_data = DataTypes.get_data_from_content(file, self.data_type)
        if self.insert_pack is not None:
            file_data = {self.insert_pack: file_data}
        return Sorting.sort_everything(file_data)
