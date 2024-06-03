from typing import Any

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataTypes as DataTypes
import DataMiners.GrabSingleFile.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabSingleFileDataMiner0(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("file_display_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    def initialize(self, **kwargs) -> None:
        if "data_type" not in kwargs:
            self.data_type = DataTypes.DataTypes.json
        else:
            self.data_type = DataTypes.DataTypes[kwargs["data_type"]]
        self.location:str = kwargs["location"]
        self.file_display_name:str|None = kwargs["file_display_name"]
        self.insert_pack:str|None = kwargs.get("insert_pack", None)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:

        exception = None
        try:
            file = self.get_accessor("client").read(self.location, self.data_type.get_data_format())
        except FileNotFoundError as e:
            exception = e
            if self.file_display_name is None:
                exception_message = "No file found in \"%s\"" % (self.version)
            else:
                exception_message = "No %s file found in \"%s\"!" % (self.file_display_name, self.version)
            exception.args = tuple(list(exception.args) + [exception_message])
        if exception is not None:
            raise exception

        file_data = DataTypes.get_data_from_content(file, self.data_type)
        if self.insert_pack is not None:
            file_data = {self.insert_pack: file_data}
        return Sorting.sort_everything(file_data)
