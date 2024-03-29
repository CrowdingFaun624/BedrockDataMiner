import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.ResourcePacks.ResourcePacksDataMiner as ResourcePacksDataMiner

class ResourcePacksDataMiner0(ResourcePacksDataMiner.ResourcePacksDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "resource_packs_folder": (str, True),
    })

    def initialize(self, **kwargs) -> None:
        self.resource_packs_folder:str = kwargs["resource_packs_folder"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.ResourcePackTypedDict]:
        resource_pack_data = ResourcePacksDataMiner.get_resource_pack_order()
        resource_pack_order, resource_pack_tags = resource_pack_data["order"], resource_pack_data["types"]
        resource_pack_order_dict = {name: index for index, name in enumerate(resource_pack_order)} # So I don't have to index it a whole twelve times
        file_list = self.get_file_list()
        resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = []
        resource_pack_names:set[str] = set()

        for file in file_list:
            assert not file.startswith("/") # just in case one of the InstallManagers goes wonky.
            if file.startswith(self.resource_packs_folder):
                if file.count("/") == 1: continue # random file in resource packs folder, such as "flipbook_textures.json" in a0.16.0_build3
                name = file.split("/")[1]
                if name == "": continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in resource_pack_order:
                    raise RuntimeError("Unknown resource pack name in \"%s\": \"%s\"" % (self.version.name, name))
                if name in resource_pack_names: continue # so they aren't recorded multiple times - wonky behavior
                resource_pack_names.add(name)
                resource_packs.append({"name": name, "tags": resource_pack_tags[name], "id": resource_pack_order_dict[name]})
        
        if len(resource_packs) == 0:
            raise RuntimeError("No resource packs found in \"%s\"!" % self.version.name)
        return sorted(resource_packs, key=lambda pack: pack["id"])
