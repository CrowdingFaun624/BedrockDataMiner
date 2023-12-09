from typing import Any

import DataMiners.ResourcePacks.ResourcePacksDataMiner as ResourcePacksDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class ResourcePacksDataMiner0(ResourcePacksDataMiner.ResourcePacksDataMiner):
    def activate(self, dependency_data:dict[str,Any]|None=None) -> list[DataMinerTyping.ResourcePackTypedDict]:
        resource_pack_data = self.get_resource_pack_order()
        resource_pack_order, resource_pack_tags = resource_pack_data["order"], resource_pack_data["types"]
        resource_pack_order_dict = {name: index for index, name in enumerate(resource_pack_order)} # So I don't have to index it a whole twelve times
        file_list = self.get_file_list()
        resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = []
        resource_pack_names:set[str] = set()

        for file in file_list:
            assert not file.startswith("/") # just in case one of the InstallManagers goes wonky.
            if file.startswith("resource_packs"):
                name = file.split("/")[1]
                if name not in resource_pack_order:
                    raise RuntimeError("Unknown resource pack name in \"%s\": \"%s\"" % (self.version.name, name))
                if name in resource_pack_names: continue # so they aren't recorded multiple times - wonky behavior
                resource_pack_names.add(name)
                resource_packs.append({"name": name, "tags": resource_pack_tags[name], "id": resource_pack_order_dict[name]})
        
        if len(resource_packs) == 0:
            raise RuntimeError("No resource packs found in \"%s\"!" % self.version.name)
        sorted_resource_packs = sorted(resource_packs, key=lambda pack: pack["id"])
        return sorted_resource_packs
