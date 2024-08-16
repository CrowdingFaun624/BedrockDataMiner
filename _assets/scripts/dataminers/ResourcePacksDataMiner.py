import enum
from typing import TypedDict

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.DataFile as DataFile
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["ResourcePacksDataMiner"]

class ResourcePackTypedDict(TypedDict):
    name: str
    tags: list[str]

class ResourcePackTag(enum.Enum):
    core = "core"
    education = "education"
    experimental = "experimental"
    extra = "extra"
    vanity = "vanity"

type_verifier = TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.EnumTypeVerifier(set(tag.name for tag in ResourcePackTag)), list, "a str", "a list"))
), list, "a dict", "a list")

def get_resource_pack_order() -> list[ResourcePackTypedDict]:
    data = DataFile.data_files["resource_pack_data"].contents
    type_verifier.base_verify(data)
    return data

resource_pack_order = {resource_pack["name"]: index for index, resource_pack in enumerate(get_resource_pack_order())}

class ResourcePacksDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("resource_packs_directory", "a str", True, str),
    )

    def initialize(self, resource_packs_directory:str) -> None:
        self.resource_packs_directory = resource_packs_directory

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.ResourcePackTypedDict]:
        file_list = self.get_accessor("client").get_file_list()
        resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = []
        resource_pack_names:set[str] = set()

        unrecognized_resource_packs:set[str] = set()
        for file in file_list:
            if file.startswith(self.resource_packs_directory):
                if file.count("/") == 1: continue # random file in resource packs directory, such as "flipbook_textures.json" in a0.16.0_build3
                name = file.split("/")[1]
                if name == "": continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in resource_pack_order:
                    unrecognized_resource_packs.add(name)
                    continue
                if name in resource_pack_names: continue # so they aren't recorded multiple times - wonky behavior
                resource_pack_names.add(name)
                resource_packs.append({"name": name, "path": "%s/%s/" % (self.resource_packs_directory, name)})

        if len(unrecognized_resource_packs) > 0:
            raise Exceptions.UnrecognizedPackError(sorted(unrecognized_resource_packs), "resource", self)
        if len(resource_packs) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return sorted(resource_packs, key=lambda pack: resource_pack_order[pack["name"]])
