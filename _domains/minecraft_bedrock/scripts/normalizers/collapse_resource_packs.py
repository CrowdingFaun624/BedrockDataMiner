import enum
from collections import defaultdict
from typing import Any, Iterable, Literal, Mapping, Optional, Sequence, TypedDict

from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import Serializer
from Utilities.Exceptions import DataminerException, message
from Utilities.File import AbstractFile, FakeFile
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

domain = get_domain_from_module(__name__)

class UnrecognizedPackError(DataminerException):
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
        return f"{self.PACK_TYPES[self.pack_type]} {f"\"{self.pack}\"" if isinstance(self.pack, str) else f"[{", ".join(f"\"{pack}\"" for pack in self.pack)}]"}{message(self.source, "", ", found by %s,")} is not recognized{message(self.message)}"

class ResourcePackTypedDict(TypedDict):
    name: str
    tags: list[str]

class ResourcePackTag(enum.Enum):
    core = "core"
    education = "education"
    experimental = "experimental"
    extra = "extra"
    vanity = "vanity"

type_verifier = ListTypeVerifier(TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("name", True, str),
    TypedDictKeyTypeVerifier("tags", True, ListTypeVerifier(EnumTypeVerifier(set(tag.name for tag in ResourcePackTag)), list))
), list)

def get_resource_pack_order() -> list[ResourcePackTypedDict]:
    data = get_domain_from_module(__name__).data_files["resource_pack_data"].contents
    type_verifier.verify_throw(data)
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

def get_resource_packs_by_tag(data:Mapping[str,Any]) -> Iterable[tuple[str,list[str]]]:
    resource_packs_by_tag:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack in data.keys():
        tag_string = resource_pack_tag_strings.get(resource_pack)
        if tag_string is None:
            raise UnrecognizedPackError(resource_pack, "pack")
        resource_packs_by_tag[tag_string].append(resource_pack)
    return resource_packs_by_tag.items()

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("add_defined_in", False, bool),
))
def collapse_resource_packs_dict[a](data:Mapping[str,Mapping[str,a]], add_defined_in:bool=True) -> dict[str,dict[str,a]]:
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
    return dict(output)

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("add_defined_in", False, bool),
    TypedDictKeyTypeVerifier("serializer", False, str),
))
def collapse_resource_packs_dict_file[a](data:Mapping[str,AbstractFile[Mapping[str,a]]], serializer:str="minecraft_common!serializers/json") -> FakeFile[dict[str,dict[str,a]]]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.'''
    output:defaultdict[str,dict[str,a]] = defaultdict(lambda: {})
    file_hashes:list[int] = []
    _serializer = domain.script_referenceable.get(serializer, Serializer)
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            file_hashes.append(hash(file))
            output[tag_string].update(file.read(_serializer))
    return FakeFile("combined_file", dict(output), None, hash(tuple(file_hashes)))

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", False, str),
))
def collapse_resource_packs_list2_file[a](data:Mapping[str,AbstractFile[Sequence[a]]], serializer:str="minecraft_common!serializers/json") -> FakeFile[dict[str,list[a]]]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.'''
    output:defaultdict[str,list[a]] = defaultdict(lambda: [])
    file_hashes:list[int] = []
    _serializer = domain.script_referenceable.get(serializer, Serializer)
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            file_hashes.append(hash(file))
            output[tag_string].extend(file.read(_serializer))
    return FakeFile("combined_file", dict(output), None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def collapse_resource_packs_flat[a](data:Mapping[str,a]) -> dict[str,a]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.'''
    output:dict[str,a] = {}
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string] = data[resource_pack]
    return output

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", False, str),
))
def collapse_resource_packs_list_file[a](data:Mapping[str,AbstractFile[Sequence[a]]], serializer:str="minecraft_common!serializers/json") -> FakeFile[dict[str,list[a]]]:
    '''
    Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    '''
    output:defaultdict[str,list[a]] = defaultdict(lambda: [])
    file_hashes:list[int] = []
    _serializer = domain.script_referenceable.get(serializer, Serializer)
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            output[tag_string].extend(file.read(_serializer))
            file_hashes.append(hash(file))
    return FakeFile("combined_file", dict(output), None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def collapse_resource_pack_names(data:Sequence[str]) -> list[str]:
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
