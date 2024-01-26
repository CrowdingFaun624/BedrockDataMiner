import pyjson5

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Items.ItemsDataMiner as ItemsDataMiner

class ItemsDataMiner0(ItemsDataMiner.ItemsDataMiner):
    def initialize(self, **kwargs) -> None:
        if "behavior_packs_location" in kwargs:
            self.behavior_packs_location:str|None = kwargs["behavior_packs_location"]
        else:
            raise ValueError("`ItemsDataMiner0` was initialized without kwarg \"behavior_packs_location\"!")
    
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Items:
        behavior_packs = dependency_data["behavior_packs"]
        item_files:dict[tuple[str,str],str] = {}
        for behavior_pack in behavior_packs:
            behavior_path_items_path = "%s/%s/items/" % (self.behavior_packs_location, behavior_pack["name"])
            for item_path in self.get_files_in(behavior_path_items_path):
                assert item_path.endswith(".json")
                item_name = item_path.replace(behavior_path_items_path, "", 1).replace(".json", "", 1)
                assert not item_name.endswith(".json")
                item_files[item_name, behavior_pack["name"]] = item_path
        output:DataMinerTyping.Items = {}
        for (item_name, behavior_pack_name), item_path in item_files.items():
            item_data = pyjson5.loads(self.read_file(item_path))
            if item_name not in output:
                output[item_name] = {behavior_pack_name: item_data}
            else:
                output[item_name][behavior_pack_name] = item_data
        return output
