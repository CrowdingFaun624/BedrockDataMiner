# The json is invalid in very old versions, this tries to correct that.

from typing import Any, Callable

import pyjson5  # supports comments

import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

location_function:Callable[[str,str],tuple[bool,str]] = lambda key, value: (value.endswith("/"), "location does not end in \"/\"")

# NOTE: this is unused for now until I implement custom serializers/deserializers.

class ModelsDataMiner(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=location_function),
    )

    def initialize(self, location:str) -> None:
        self.location = location

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        files:dict[tuple[str,str],str] = {}
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        for pack in packs:
            path_base = pack["path"] + self.location
            for path in accessor.get_files_in(path_base):
                if not path.endswith(".json"):
                    raise Exceptions.DataMinerUnrecognizedSuffixError(self, path, ["json"])
                file_name = path.replace(path_base, "", 1).replace(".json", "", 1)
                if file_name.endswith(".json"):
                    raise Exceptions.InvalidStateError(self, "file_name still ends in \".json\"!")
                files[file_name, pack["name"]] = path

        output:dict[str,dict[str,Any]] = {}
        remove = "\r\n\r\n}\r\n"
        for (file_name, pack_name), path in files.items():
            file_bits:str = accessor.read(path, "t")
            if not file_bits.endswith(remove):
                raise Exceptions.DataMinerFailureError(self, "ModelsDataMiner0 is being used unnecessarily! File ends with: %s" % pyjson5.dumps(file_bits[-20:]))
            file_bits = file_bits[:-len(remove)]
            file_data = pyjson5.loads(file_bits)
            if file_name not in output:
                output[file_name] = {pack_name: file_data}
            else:
                output[file_name][pack_name] = file_data

        if len(output) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        return Sorting.sort_everything(output)
