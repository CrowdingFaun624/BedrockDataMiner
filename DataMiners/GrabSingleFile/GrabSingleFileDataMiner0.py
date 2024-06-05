from typing import Any

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataTypes as DataTypes
import DataMiners.GrabSingleFile.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabSingleFileDataMiner0(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    def initialize(self, **kwargs) -> None:
        self.data_type = DataTypes.DataTypes[kwargs.get("data_type", "json")]
        self.location:str = kwargs["location"]
        self.insert_pack:str|None = kwargs.get("insert_pack", None)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client")
        if not accessor.file_exists(self.location):
            raise Exceptions.DataMinerNothingFoundError(self)
        file = self.get_accessor("client").read(self.location, self.data_type.get_data_format())

        file_data = DataTypes.get_data_from_content(file, self.data_type)
        if self.insert_pack is not None:
            file_data = {self.insert_pack: file_data}
        return Sorting.sort_everything(file_data)
