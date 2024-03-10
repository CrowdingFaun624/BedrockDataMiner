# The json is invalid in very old versions, this tries to correct that.

import pyjson5 # supports comments
from typing import Any

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.Models.ModelsDataMiner as ModelsDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class ModelsDataMiner0(ModelsDataMiner.ModelsDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "location": (str, True),
    })

    def initialize(self, **kwargs) -> None:
        self.location:str = kwargs["location"]
        if not self.location.endswith("/"):
            raise ValueError("\"location\" \"%s\" does not end in \"/\"!" % (self.location))

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        packs = dependency_data["resource_packs"]
        files:dict[tuple[str,str],str] = {}
        for pack in packs:
            path_base = self.location % pack["name"]
            for path in self.get_files_in(path_base):
                if not path.endswith(".json"):
                    raise ValueError("Unrecognized suffix on path \"%s\"!" % path)
                file_name = path.replace(path_base, "", 1).replace(".json", "", 1)
                assert not file_name.endswith(".json")
                files[file_name, pack["name"]] = path

        output:dict[str,dict[str,Any]] = {}
        remove = "\r\n\r\n}\r\n"
        for (file_name, pack_name), path in files.items():
            file_bits:str = self.read_file(path)
            if not file_bits.endswith(remove):
                raise RuntimeError("ModelsDataMiner0 is being used unnecessarily! File ends with: %s" % pyjson5.dumps(file_bits[-20:]))
            file_bits = file_bits[:-len(remove)]
            file_data = pyjson5.loads(file_bits)
            if file_name not in output:
                output[file_name] = {pack_name: file_data}
            else:
                output[file_name][pack_name] = file_data

        if len(output) == 0:
            raise FileNotFoundError("No models files found in \"%s\"" % (self.version))

        return Sorting.sort_everything(output)
