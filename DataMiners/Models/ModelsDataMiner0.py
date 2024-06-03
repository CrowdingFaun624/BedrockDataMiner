# The json is invalid in very old versions, this tries to correct that.

from typing import Any

import pyjson5  # supports comments

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.Models.ModelsDataMiner as ModelsDataMiner
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class ModelsDataMiner0(ModelsDataMiner.ModelsDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.location:str = kwargs["location"]
        if not self.location.endswith("/"):
            raise ValueError("\"location\" \"%s\" does not end in \"/\"!" % (self.location))

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        packs = environment.dependency_data["resource_packs"]
        assert packs is not None
        files:dict[tuple[str,str],str] = {}
        accessor = self.get_accessor("client")
        for pack in packs:
            path_base = pack["path"] + self.location
            for path in accessor.get_files_in(path_base):
                if not path.endswith(".json"):
                    raise ValueError("Unrecognized suffix on path \"%s\"!" % path)
                file_name = path.replace(path_base, "", 1).replace(".json", "", 1)
                assert not file_name.endswith(".json")
                files[file_name, pack["name"]] = path

        output:dict[str,dict[str,Any]] = {}
        remove = "\r\n\r\n}\r\n"
        for (file_name, pack_name), path in files.items():
            file_bits:str = accessor.read(path, "t")
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
