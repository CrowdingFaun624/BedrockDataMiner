import enum
from collections import defaultdict
from typing import Any, Iterable, Literal, Optional, TypedDict

import Utilities.DataFile as DataFile
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class UnrecognizedPackError(Exceptions.DataMinerException):
    "The behavior pack/resource pack is not recognized."

    PACK_TYPES:defaultdict[str,str] = defaultdict(lambda: "Pack", {"behavior": "Behavior pack", "resource": "Resource pack", "skin": "Skin pack", "emote": "Emote directory", "piece": "Piece directory"})

    def __init__(self, pack:str|list[str], pack_type:Literal["behavior", "resource", "skin", "emote", "piece", "pack"], source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :pack: The name(s) of the behavior pack/resource pack(s).
        :pack_type: The type of pack ("behavior", "resource", "skin", "emote", "piece", or "pack").
        :source: The object that found the behavior pack/resource pack.
        :message: Additional text to place after the main message.
        '''
        super().__init__(pack, pack_type, source, message)
        self.pack = pack
        self.pack_type = pack_type
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"{self.PACK_TYPES[self.pack_type]} {f"\"{self.pack}\"" if isinstance(self.pack, str) else f"[{", ".join(f"\"{pack}\"" for pack in self.pack)}]"}{Exceptions.message(self.source, "", ", found by %s,")} is not recognized{Exceptions.message(self.message)}"

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

def get_resource_pack_tag_strings() -> dict[str, str]:
    '''
    Makes sure that identical strings have the same identity.
    '''
    output:dict[str,str] = {}
    already_tags:dict[str,str] = {} # mapping from string to the same string.
    for resource_pack_name, resource_pack in resource_pack_dict.items():
        tag_str = ",".join(resource_pack["tags"])
        if tag_str in already_tags: # evil code
            tag_str = already_tags[tag_str]
        else:
            already_tags[tag_str] = tag_str
        output[resource_pack_name] = tag_str
    return output

resource_pack_data = get_resource_pack_order()
resource_pack_order = {resource_pack["name"]: index for index, resource_pack in enumerate(resource_pack_data)}
resource_pack_dict = {resource_pack_name: resource_pack for resource_pack_name, resource_pack in zip(resource_pack_order, resource_pack_data)}
resource_pack_tag_strings = get_resource_pack_tag_strings()

def get_resource_packs_by_tag(data:dict[str,Any]) -> Iterable[tuple[str,list[str]]]:
    resource_packs_by_tag:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack in data.keys():
        tag_string = resource_pack_tag_strings.get(resource_pack)
        if tag_string is None:
            raise UnrecognizedPackError(resource_pack, "pack")
        resource_packs_by_tag[tag_string].append(resource_pack)
    return resource_packs_by_tag.items()
