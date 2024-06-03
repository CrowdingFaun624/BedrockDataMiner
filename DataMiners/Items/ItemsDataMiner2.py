from typing import Any

import pyjson5

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Items.ItemsDataMiner as ItemsDataMiner
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class ItemsDataMiner2(ItemsDataMiner.ItemsDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.location:str = kwargs["location"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:

        exception = None
        try:
            file = self.get_accessor("client").read(self.location, "t")
        except FileNotFoundError as e:
            exception = e
            exception.args = tuple(list(exception.args) + ["No items file found in \"%s\"!" % (self.version)])
        if exception is not None:
            raise exception

        items:list[dict[str,Any]] = pyjson5.loads(file)
        output:DataMinerTyping.Items = {}
        for item_properties in items:
            item_name:str = item_properties["name"]
            del item_properties["name"]
            output[item_name] = {"vanilla": item_properties}
        return Sorting.sort_everything(output)
