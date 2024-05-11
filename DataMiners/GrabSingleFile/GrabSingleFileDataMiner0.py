from typing import Any

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.DataTypes as DataTypes
import DataMiners.GrabSingleFile.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import Utilities.Sorting as Sorting

class GrabSingleFileDataMiner0(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "data_type": (DataMinerParameters.LiteralParameters(DataTypes.DataTypes.data_types()), False),
        "location": (str, True),
        "file_display_name": (str, True),
        "insert_pack": (str, False),
    })

    def initialize(self, **kwargs) -> None:
        if "data_type" not in kwargs:
            self.data_type = DataTypes.DataTypes.json
        else:
            self.data_type = DataTypes.DataTypes[kwargs["data_type"]]
        self.location:str = kwargs["location"]
        self.file_display_name:str|None = kwargs["file_display_name"]
        self.insert_pack:str|None = kwargs.get("insert_pack", None)

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> Any:

        exception = None
        try:
            file = self.read_file(self.location)
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
