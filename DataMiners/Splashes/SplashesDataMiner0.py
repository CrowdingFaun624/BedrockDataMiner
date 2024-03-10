import pyjson5 # supports comments
from typing import Callable, IO

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.Splashes.SplashesDataMiner as SplashesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class SplashesDataMiner0(SplashesDataMiner.SplashesDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "splashes_locations": (DataMinerParameters.ListParameters(str), True),
    })

    def initialize(self, **kwargs) -> None:
        self.splashes_locations = kwargs["splashes_locations"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Splashes:
        resource_packs = dependency_data["resource_packs"]
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files:dict[str,str] = {}
        for splashes_location in self.splashes_locations:
            resource_pack_files.update({splashes_location % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names})
        loader:Callable[[IO[bytes]],dict] = lambda file: pyjson5.loads(file.read().decode())
        files_request = [(resource_pack_file, "b", pyjson5.load) for resource_pack_file in resource_pack_files.keys()]
        files:dict[str,DataMinerTyping.SplashesFile] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No \"splashes.json\" files found in \"%s\"" % self.version)
        
        output:DataMinerTyping.Splashes = {}
        for resource_pack_file, splashes in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            if not isinstance(splashes, dict):
                raise TypeError("Splashes for resource pack \"%s\" in version \"%s\" is not a dict!" % (resource_pack_name, self.version))
            if list(splashes.keys()) != ["splashes"]:
                raise KeyError("Unrecognized key(s) are within resource pack \"%s\" of version \"%s\": %s" % (resource_pack_name, self.version, list(splashes.keys())))
            splash_list = splashes["splashes"]
            output[resource_pack_name] = splash_list
        return Sorting.sort_everything(output)
