from typing import Any

import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["SplashesDataMiner0"]

class SplashesDataMiner0(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def initialize(self, locations:list[str]) -> None:
        super().initialize(locations, "resource_packs")

    def get_output(self, files: dict[str,DataMinerTyping.SplashesFile], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str, Any]:
        output:DataMinerTyping.Splashes = {}
        for resource_pack_file, splashes in files.items():
            resource_pack_name = pack_files[resource_pack_file]
            if not isinstance(splashes, dict):
                raise Exceptions.DataMinerFailureError(self, "Splashes for resource pack \"%s\" is not a dict!" % (resource_pack_name,))
            if list(splashes.keys()) != ["splashes"]:
                raise Exceptions.DataMinerFailureError(self, "Unrecognized key(s) are within resource pack \"%s\": %s" % (resource_pack_name, list(splashes.keys())))
            splash_list = splashes["splashes"]
            output[resource_pack_name] = splash_list
        return output
