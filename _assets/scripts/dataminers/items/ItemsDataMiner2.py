from typing import Any

import _assets.scripts.dataminers.MyGrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["ItemsDataMiner2"]

class ItemsDataMiner2(GrabSingleFileDataMiner.MyGrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, location:str) -> None:
        super().initialize(location, insert_pack="vanilla")

    def get_output(self, file:list[dict[str,Any]], environment: DataMinerEnvironment.DataMinerEnvironment) -> Any:
        output:dict[str,dict[str,Any]] = {}
        for item_properties in file:
            item_name:str = item_properties["name"]
            del item_properties["name"]
            output[item_name] = {"vanilla": item_properties}
        return output
