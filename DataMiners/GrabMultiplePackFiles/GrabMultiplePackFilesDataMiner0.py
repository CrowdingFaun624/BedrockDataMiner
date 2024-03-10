import pyjson5 # supports comments
from typing import Any

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.GrabMultiplePackFiles.GrabMultiplePackFilesDataMiner as GrabMultiplePackFilesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class GrabMultiplePackFilesDataMiner0(GrabMultiplePackFilesDataMiner.GrabMultiplePackFilesDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "location": (str, True),
        "pack_type": (DataMinerParameters.LiteralParameters({"resource_packs", "behavior_packs"}), True),
        "suffixes": (DataMinerParameters.ListParameters(str), False),
        "file_display_name": ((str, type(None)), True),
    })

    def initialize(self, **kwargs) -> None:
        self.location:str = kwargs["location"]
        if not self.location.endswith("/"):
            raise ValueError("\"location\" \"%s\" does not end in \"/\"!" % (self.location))
        self.pack_type:str = kwargs["pack_type"]
        if "suffixes" in kwargs:
            self.suffixes:list[str]|None = kwargs["suffixes"]
        else:
            self.suffixes = None
        self.file_display_name:str|None = kwargs["file_display_name"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        packs = dependency_data[self.pack_type]
        files:dict[tuple[str,str],str] = {}
        for pack in packs:
            path_base = self.location % pack["name"]
            for path in self.get_files_in(path_base):
                if self.suffixes is None:
                    file_name = path.replace(path_base, "", 1)
                    files[file_name, pack["name"]] = path
                else:
                    suffixes = [suffix for suffix in self.suffixes if path.endswith("." + suffix)]
                    if len(suffixes) == 0:
                        raise ValueError("Unrecognized suffix on path \"%s\"!" % path)
                    suffix = "." + suffixes[0]
                    file_name = path.replace(path_base, "", 1).replace(suffix, "", 1)
                    assert not file_name.endswith(suffix)
                    files[file_name, pack["name"]] = path

        output:dict[str,dict[str,Any]] = {}
        for (file_name, pack_name), path in files.items():
            file_bits = self.read_file(path)
            if len(file_bits) <= 1: continue
            file_data = pyjson5.loads(file_bits)
            if file_name not in output:
                output[file_name] = {pack_name: file_data}
            else:
                output[file_name][pack_name] = file_data

        if len(output) == 0:
            if self.file_display_name is None:
                raise FileNotFoundError("No files found in \"%s\"" % self.version)
            else:
                raise FileNotFoundError("No %s files found in \"%s\"" % (self.file_display_name, self.version))

        return Sorting.sort_everything(output)
