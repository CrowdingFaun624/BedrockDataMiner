import enum
from collections import defaultdict
from typing import Any, Iterable, Literal, Optional, TypedDict

import Domain.Domains as Domains
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier

__all__ = [
    "collapse_resource_packs_dict",
    "collapse_resource_packs_dict_file",
    "collapse_resource_packs_flat",
    "collapse_resource_packs_list",
    "collapse_resource_packs_list_file",
    "collapse_resource_pack_names",
]

class UnrecognizedPackError(Exceptions.DataminerException):
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
    data = Domains.get_domain_from_module(__name__).data_files["resource_pack_data"].contents
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

def collapse_resource_packs_dict[a](data:dict[str,dict[str,a]], add_defined_in:bool=True) -> dict[str,dict[str,a]]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    Also adds a "defined_in" tag to each resource pack's properties unless `add_defined_in` is False.'''
    output:defaultdict[str,dict[str,a]] = defaultdict(lambda: {})
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string].update(data[resource_pack])
            if add_defined_in:
                defined_in_key = output[tag_string].get("defined_in")
                if defined_in_key is None:
                    output[tag_string]["defined_in"] = [resource_pack] # type: ignore
                else:
                    defined_in_key.append(resource_pack) # type: ignore
    return type(data)(output)

def collapse_resource_packs_dict_file[a](data:dict[str,File.AbstractFile[dict[str,a]]], add_defined_in:bool=True) -> File.FakeFile[dict[str,dict[str,a]]]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    Also adds a "defined_in" tag to each resource pack's properties unless `add_defined_in` is False.'''
    output:defaultdict[str,dict[str,a]] = defaultdict(lambda: {})
    file_hashes:list[int] = []
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            file_hashes.append(hash(file))
            output[tag_string].update(file.data)
            if add_defined_in:
                defined_in_key = output[tag_string].get("defined_in")
                if defined_in_key is None:
                    output[tag_string]["defined_in"] = [resource_pack] # type: ignore
                else:
                    defined_in_key.append(resource_pack) # type: ignore
    return File.FakeFile("combined_file", type(data)(output), hash(tuple(file_hashes))) # type: ignore

def collapse_resource_packs_flat[a](data:dict[str,a]) -> dict[str,a]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.'''
    output:dict[str,a] = {}
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string] = data[resource_pack]
    return output

def collapse_resource_packs_list_file[a](data:dict[str,File.AbstractFile[list[a]]]) -> File.FakeFile[dict[str,list[a]]]:
    '''
    Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    '''
    output:defaultdict[str,list[a]] = defaultdict(lambda: [])
    file_hashes:list[int] = []
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            output[tag_string].extend(file.data)
            file_hashes.append(hash(file))
    return File.FakeFile("combined_file", dict(output), hash(tuple(file_hashes)))

def collapse_resource_packs_list[a](data:dict[str,list[a]]) -> dict[str,list[a]]:
    '''
    Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    '''
    output:defaultdict[str,list[a]] = defaultdict(lambda: [])
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string].extend(data[resource_pack])
    return dict(output)

def collapse_resource_pack_names(data:list[str]) -> list[str]:
    output:list[str] = []
    exists_in_output:set[int] = set() # set of IDs because values of resource_pack_tag_strings are always the same.
    for properties_resource_pack in data:
        tag_str = resource_pack_tag_strings.get(properties_resource_pack)
        if tag_str is None:
            raise UnrecognizedPackError(properties_resource_pack, "pack")
        if (tag_str_id := id(tag_str)) not in exists_in_output:
            exists_in_output.add(tag_str_id)
            output.append(tag_str)
    return list(reversed(output)) # reversed so it behaves the same as it does before refactor.
