from typing import Any

import pyjson5

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.Items.ItemsDataMiner as ItemsDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class ItemsDataMiner2(ItemsDataMiner.ItemsDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.location:str = kwargs["location"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:

        accessor = self.get_accessor("client")
        if not accessor.file_exists(self.location):
            raise Exceptions.DataMinerNothingFoundError(self)
        file = self.get_accessor("client").read(self.location, "t")

        items:list[dict[str,Any]] = pyjson5.loads(file)
        output:DataMinerTyping.Items = {}
        for item_properties in items:
            item_name:str = item_properties["name"]
            del item_properties["name"]
            output[item_name] = {"vanilla": item_properties}
        return Sorting.sort_everything(output)
