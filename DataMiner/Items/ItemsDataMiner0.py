from typing import IO, Any, Callable, cast

import pyjson5  # supports comments

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.Items.ItemsDataMiner as ItemsDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class ItemsDataMiner0(ItemsDataMiner.ItemsDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
    )

    def initialize(self, **kwargs) -> None:
        self.locations:list[str] = kwargs["locations"]
        self.pack_type:str = kwargs["pack_type"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Items:
        resource_packs:DataMinerTyping.ResourcePacks|DataMinerTyping.BehaviorPacks = environment.dependency_data.get(self.pack_type, self)
        resource_pack_names = [(resource_pack["name"], resource_pack["path"]) for resource_pack in resource_packs]
        resource_pack_files:dict[str,str] = {}
        for items_location in self.locations:
            resource_pack_files.update({resource_pack_path + items_location: resource_pack_name for resource_pack_name, resource_pack_path in resource_pack_names})
        files_request = [(resource_pack_file, "t", cast(Callable[[IO[str]],Any], pyjson5.load)) for resource_pack_file in resource_pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,DataMinerTyping.Items] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        items:DataMinerTyping.Items = {}
        for resource_pack_file, resource_pack_items in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            if set(resource_pack_items.keys()) != {"items"}:
                raise Exceptions.DataMinerFailureError(self, "Unknown key(s) in \"items.json\" in resource pack \"%s\": %s" % (resource_pack_name, resource_pack_items.keys()))
            for item_name, item_properties in resource_pack_items["items"].items():
                if item_name not in items:
                    items[item_name] = {resource_pack_name: item_properties}
                else:
                    items[item_name][resource_pack_name] = item_properties
        return Sorting.sort_everything(items)
