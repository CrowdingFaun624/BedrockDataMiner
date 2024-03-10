import pyjson5 # supports comments
from typing import Any

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.GrabMultipleFiles.GrabMultipleFilesDataMiner as GrabMultipleFilesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

def a(aa:tuple[type,...]) -> None: pass
a((str, type(None)))

class GrabMultipleFilesDataMiner0(GrabMultipleFilesDataMiner.GrabMultipleFilesDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "location": (str, True),
        "suffixes": (DataMinerParameters.ListParameters(str), False),
        "file_display_name": ((str, type(None)), True),
        "insert_pack": (str, False),
    })

    def initialize(self, **kwargs) -> None:
        self.location:str = kwargs["location"]
        if not self.location.endswith("/"):
            raise ValueError("\"location\" \"%s\" does not end in \"/\"!" % (self.location))
        if "suffixes" in kwargs:
            self.suffixes:list[str]|None = kwargs["suffixes"]
        else:
            self.suffixes = None
        self.file_display_name:str|None = kwargs["file_display_name"]
        if "insert_pack" in kwargs:
            self.insert_pack:str|None = kwargs["insert_pack"]
        else:
            self.insert_pack = None

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        files:dict[str,str] = {}
        path_base = self.location
        for path in self.get_files_in(path_base):
            if self.suffixes is None:
                file_name = path.replace(path_base, "", 1)
                files[file_name] = path
            else:
                suffixes = [suffix for suffix in self.suffixes if path.endswith("." + suffix)]
                if len(suffixes) == 0:
                    raise ValueError("Unrecognized suffix on path \"%s\"!" % path)
                suffix = "." + suffixes[0]
                file_name = path.replace(path_base, "", 1).replace(suffix, "", 1)
                assert not file_name.endswith(suffix)
                files[file_name] = path
        if len(files) == 0:
            if self.file_display_name is None:
                raise FileNotFoundError("No files found in \"%s\"" % self.version)
            else:
                raise FileNotFoundError("No %s files found in \"%s\"" % (self.file_display_name, self.version))

        output:dict[str,dict[str,Any]] = {}
        for file_name, path in files.items():
            file_data = pyjson5.loads(self.read_file(path))
            if self.insert_pack is None:
                output[file_name] = file_data
            else:
                output[file_name] = {self.insert_pack: file_data}
        return Sorting.sort_everything(output)
