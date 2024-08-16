import enum
from typing import Literal, TypedDict

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.DataFile as DataFile
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["PacksDataMiner"]

class PackTypedDict(TypedDict):
    name: str
    tags: list[str]

class PackTag(enum.Enum):
    core = "core"
    education = "education"
    experimental = "experimental"
    extra = "extra"
    vanity = "vanity"

type_verifier = TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.EnumTypeVerifier(set(tag.name for tag in PackTag)), list, "a str", "a list"))
), list, "a dict", "a list")

def get_pack_order() -> list[PackTypedDict]:
    data = DataFile.data_files["resource_pack_data"].contents
    type_verifier.base_verify(data)
    return data

pack_order = {resource_pack["name"]: index for index, resource_pack in enumerate(get_pack_order())}

class PacksDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("directory", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier({"resource", "behavior"}))
    )

    def initialize(self, directory:str, pack_type:Literal["resource", "behavior"]) -> None:
        self.directory = directory
        self.pack_type:Literal["resource", "behavior"] = pack_type

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.ResourcePackTypedDict]:
        file_list = self.get_accessor("client").get_file_list()
        packs:list[DataMinerTyping.ResourcePackTypedDict] = []
        pack_names:set[str] = set()

        unrecognized_packs:set[str] = set()
        for file in file_list:
            if file.startswith(self.directory):
                if file.count("/") == 1: continue # random file in resource packs directory, such as "flipbook_textures.json" in a0.16.0_build3
                name = file.split("/")[1]
                if name == "": continue # relic in old archive.org minecraft-iOS versions. Just a file with no content (b'')
                if name not in pack_order:
                    unrecognized_packs.add(name)
                    continue
                if name in pack_names: continue # so they aren't recorded multiple times - wonky behavior
                pack_names.add(name)
                packs.append({"name": name, "path": "%s/%s/" % (self.directory, name)})

        if len(unrecognized_packs) > 0:
            raise Exceptions.UnrecognizedPackError(sorted(unrecognized_packs), self.pack_type, self)
        if len(packs) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return sorted(packs, key=lambda pack: pack_order[pack["name"]])
