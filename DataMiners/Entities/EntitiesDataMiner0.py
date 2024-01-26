import pyjson5

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Entities.EntitiesDataMiner as EntitiesDataMiner

class EntitiesDataMiner0(EntitiesDataMiner.EntitiesDataMiner):
    def initialize(self, **kwargs) -> None:
        if "behavior_packs_location" in kwargs:
            self.behavior_packs_location:str|None = kwargs["behavior_packs_location"]
        else:
            raise ValueError("`EntitiesDataMiner0` was initialized without kwarg \"behavior_packs_location\"!")
    
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Entities:
        behavior_packs = dependency_data["behavior_packs"]
        entity_files:dict[tuple[str,str],str] = {}
        for behavior_pack in behavior_packs:
            behavior_path_items_path = "%s/%s/entities/" % (self.behavior_packs_location, behavior_pack["name"])
            for entity_path in self.get_files_in(behavior_path_items_path):
                assert entity_path.endswith(".json")
                entity_name = entity_path.replace(behavior_path_items_path, "", 1).replace(".json", "", 1)
                assert not entity_name.endswith(".json")
                entity_files[entity_name, behavior_pack["name"]] = entity_path
        output:DataMinerTyping.Entities = {}
        for (entity_name, behavior_pack_name), entity_path in entity_files.items():
            entity_data = pyjson5.loads(self.read_file(entity_path))
            if entity_name not in output:
                output[entity_name] = {behavior_pack_name: entity_data}
            else:
                output[entity_name][behavior_pack_name] = entity_data
        return output
