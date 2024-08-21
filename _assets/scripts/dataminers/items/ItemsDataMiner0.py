from typing import Any, Literal

import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["ItemsDataMiner0"]

class ItemsDataMiner0(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
    )

    def initialize(self, locations:list[str], pack_type:Literal["resource_packs", "behavior_packs"]) -> None:
        super().initialize(locations, pack_type)

    def get_output(self, files: dict[str, dict[str,dict[str,Any]]], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str, Any]:
        output:DataMinerTyping.Items = {}
        for file_name, items in files.items():
            pack_name = pack_files[file_name]
            if set(items.keys()) != {"items"}:
                raise Exceptions.DataMinerFailureError(self, "Unknown key(s) in \"items.json\" in resource pack \"%s\": %s" % (pack_name, items.keys()))
            for item_name, item_properties in items["items"].items():
                if item_name not in output:
                    output[item_name] = {pack_name: item_properties}
                else:
                    output[item_name][pack_name] = item_properties
        return output
