import json
from typing import Any

import DataMiners.GrabSingleFile.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class GrabSingleFileDataMiner0(GrabSingleFileDataMiner.GrabSingleFileDataMiner):
    
    def initialize(self, **kwargs) -> None:
        if "location" in kwargs:
            self.location:str = kwargs["location"]
        else:
            raise ValueError("`GrabSingleFileDataMiner0` was initialized without kwarg \"location\"!")
        if "file_display_name" in kwargs:
            self.file_display_name:str|None = kwargs["file_display_name"]
        else:
            raise ValueError("`GrabSingleFileDataMiner0` was initialized without kwarg \"file_display_name\"!")
    
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
