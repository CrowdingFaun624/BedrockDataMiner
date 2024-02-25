import pyjson5

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.EntitiesClient.EntitiesClientDataMiner as EntitiesClientDataMiner
import Utilities.Sorting as Sorting

class EntitiesClientDataMiner0(EntitiesClientDataMiner.EntitiesClientDataMiner):

    def initialize(self, **kwargs) -> None:
        if "resource_packs_location" in kwargs:
            self.resource_packs_location:str|None = kwargs["resource_packs_location"]
        else:
            raise ValueError("`EntitiesClientDataMiner0` was initialized without kwarg \"resource_packs_location\"!")

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.EntitiesClient:
        resource_packs = dependency_data["resource_packs"]
        entity_files:dict[tuple[str,str],str] = {}
        for resource_pack in resource_packs:
            resource_path_items_path = "%s/%s/entity/" % (self.resource_packs_location, resource_pack["name"])
            for entity_path in self.get_files_in(resource_path_items_path):
                assert entity_path.endswith(".json")
                entity_name = entity_path.replace(resource_path_items_path, "", 1).replace(".json", "", 1)
                assert not entity_name.endswith(".json")
                entity_files[entity_name, resource_pack["name"]] = entity_path
        output:DataMinerTyping.EntitiesClient = {}
        for (entity_name, resource_pack_name), entity_path in entity_files.items():
            entity_data = pyjson5.loads(self.read_file(entity_path))
            if entity_name not in output:
                output[entity_name] = {resource_pack_name: entity_data}
            else:
                output[entity_name][resource_pack_name] = entity_data
        return Sorting.sort_everything(output)
