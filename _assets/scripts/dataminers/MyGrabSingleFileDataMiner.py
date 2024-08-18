from typing import Any

import DataMiner.BuiltIns.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataTypes as DataTypes
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MyGrabSingleFileDataMiner"]

class MyGrabSingleFileDataMiner(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    def initialize(self, locations:str|list[str], data_type:DataTypes.DataTypes=DataTypes.DataTypes.json, insert_pack:str|None=None) -> None:
        self.locations = [locations] if isinstance(locations, str) else locations
        self.data_type = data_type
        self.insert_pack = insert_pack

    def get_output(self, file: bytes|str, environment: DataMinerEnvironment.DataMinerEnvironment) -> Any:
        file_data = super().get_output(file, environment)
        if self.insert_pack is not None:
            file_data = {self.insert_pack: file_data}
        return file_data
