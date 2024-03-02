import json
from typing import Any

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.GrabSingleFile.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class GrabSingleFileDataMiner0(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "location": (str, True),
        "file_display_name": (str, True),
    })
    
    def initialize(self, **kwargs) -> None:
        self.location:str = kwargs["location"]
        self.file_display_name:str|None = kwargs["file_display_name"]
    
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
        
        file_data = json.loads(file)
        return Sorting.sort_everything(file_data)
