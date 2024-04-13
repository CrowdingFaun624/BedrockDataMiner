import pyjson5 # supports comments
from typing import Any, Callable, cast, IO

import DataMiners.Items.ItemsDataMiner as ItemsDataMiner
import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class ItemsDataMiner1(ItemsDataMiner.ItemsDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "locations": (DataMinerParameters.ListParameters(str), True),
        "pack_type": (DataMinerParameters.LiteralParameters(["behavior_packs", "resource_packs"]), True)
    })

    def initialize(self, **kwargs) -> None:
        self.locations:list[str] = kwargs["locations"]
        self.pack_type:str = kwargs["pack_type"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Items:
        resource_packs = dependency_data[self.pack_type]
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files:dict[str,str] = {}
        for items_location in self.locations:
            resource_pack_files.update({items_location % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names})
        files_request = [(resource_pack_file, "t", cast(Callable[[IO[str]],Any], pyjson5.load)) for resource_pack_file in resource_pack_files.keys()]
        files:dict[str,list[dict[str,Any]]] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No \"items.json\" files found in \"%s\"" % self.version)

        items:DataMinerTyping.Items = {}
        for resource_pack_file, resource_pack_items in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            for item_properties in resource_pack_items:
                item_name = item_properties["name"]
                del item_properties["name"]
                if item_name not in items:
                    items[item_name] = {resource_pack_name: item_properties}
                else:
                    items[item_name][resource_pack_name] = item_properties
        return Sorting.sort_everything(items)
