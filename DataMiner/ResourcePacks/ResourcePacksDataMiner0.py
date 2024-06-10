import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.ResourcePacks.ResourcePacksDataMiner as ResourcePacksDataMiner
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class ResourcePacksDataMiner0(ResourcePacksDataMiner.ResourcePacksDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("resource_packs_directory", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.resource_packs_directory:str = kwargs["resource_packs_directory"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.ResourcePackTypedDict]:
        resource_pack_order = CollapseResourcePacks.resource_pack_order
        file_list = self.get_accessor("client").get_file_list()
        resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = []
        resource_pack_names:set[str] = set()

        for file in file_list:
            if file.startswith(self.resource_packs_directory):
                if file.count("/") == 1: continue # random file in resource packs directory, such as "flipbook_textures.json" in a0.16.0_build3
                name = file.split("/")[1]
                if name == "": continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in resource_pack_order:
                    raise Exceptions.UnrecognizedPackError(name, "resource", self)
                if name in resource_pack_names: continue # so they aren't recorded multiple times - wonky behavior
                resource_pack_names.add(name)
                resource_packs.append({"name": name, "path": "%s/%s/" % (self.resource_packs_directory, name)})
        
        if len(resource_packs) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return sorted(resource_packs, key=lambda pack: resource_pack_order[pack["name"]])
