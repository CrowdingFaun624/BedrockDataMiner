from typing import IO, Any, Callable, cast

import pyjson5  # supports comments

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.FileDataMiner as FileDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["SplashesDataMiner0"]

class SplashesDataMiner0(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("splashes_locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def initialize(self, splashes_locations:list[str]) -> None:
        self.splashes_locations = splashes_locations

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Splashes:
        resource_packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        resource_pack_names = [(resource_pack["name"], resource_pack["path"]) for resource_pack in resource_packs]
        resource_pack_files:dict[str,str] = {}
        for splashes_location in self.splashes_locations:
            resource_pack_files.update({resource_pack_path + splashes_location: resource_pack_name for resource_pack_name, resource_pack_path in resource_pack_names})
        files_request = [(resource_pack_file, "b", cast(Callable[[IO[bytes]],Any], pyjson5.load)) for resource_pack_file in resource_pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,DataMinerTyping.SplashesFile] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output:DataMinerTyping.Splashes = {}
        for resource_pack_file, splashes in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            if not isinstance(splashes, dict):
                raise Exceptions.DataMinerFailureError(self, "Splashes for resource pack \"%s\" is not a dict!" % (resource_pack_name,))
            if list(splashes.keys()) != ["splashes"]:
                raise Exceptions.DataMinerFailureError(self, "Unrecognized key(s) are within resource pack \"%s\": %s" % (resource_pack_name, list(splashes.keys())))
            splash_list = splashes["splashes"]
            output[resource_pack_name] = splash_list
        return Sorting.sort_everything(output)
