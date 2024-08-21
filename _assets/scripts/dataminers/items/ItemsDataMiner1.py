from typing import Any, Literal

import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["ItemsDataMiner1"]

class ItemsDataMiner1(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
    )

    def initialize(self, locations:list[str], pack_type:Literal["resource_packs", "behavior_packs"]) -> None:
        super().initialize(locations, pack_type)

    def get_output(self, files: dict[str, list[dict[str,str]]], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str, Any]:
        output:dict[str,dict[str,dict[str,Any]]] = {}
        for file_name, items in files.items():
            pack_name = pack_files[file_name]
            for item_properties in items:
                item_name = item_properties["name"]
                del item_properties["name"]
                if item_name not in output:
                    output[item_name] = {pack_name: item_properties}
                else:
                    output[item_name][pack_name] = item_properties
        return output
