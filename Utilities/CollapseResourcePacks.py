import enum
import json
from collections import defaultdict
from typing import Any, Callable, Iterable, TypedDict, TypeVar

import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


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
    with open(FileManager.RESOUCE_PACK_DATA_FILE, "rt") as f:
        data:list[ResourcePackTypedDict] = json.load(f)
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

empty_dict_lambda = lambda: {}
empty_list_lambda = lambda: []
a = TypeVar("a")

def make_dict_interface(has_defined_in_key:bool=True) -> Callable[[dict[str,dict[str,a]]],dict[str,dict[str,a]]]:
    def collapse_resource_packs_interface(data:dict[str,dict[str,a]]) -> dict[str,dict[str,a]]:
        return collapse_resource_packs_dict(data, has_defined_in_key)
    return collapse_resource_packs_interface

def get_resource_packs_by_tag(data:dict[str,Any]) -> Iterable[tuple[str,list[str]]]:
    resource_packs_by_tag:defaultdict[str,list[str]] = defaultdict(empty_list_lambda)
    for resource_pack in data.keys():
        tag_string = resource_pack_tag_strings.get(resource_pack)
        if tag_string is None:
            raise Exceptions.UnrecognizedPackError(resource_pack, "pack")
        resource_packs_by_tag[tag_string].append(resource_pack)
    return resource_packs_by_tag.items()

def collapse_resource_packs_list(data:dict[str,list[a]]) -> dict[str,list[a]]:
    '''
    Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    '''
    output:defaultdict[str,list[a]] = defaultdict(empty_list_lambda)
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string].extend(data[resource_pack])
    return dict(output)

def collapse_resource_packs_dict(data:dict[str,dict[str,a]], add_defined_in:bool=True) -> dict[str,dict[str,a]]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    Also adds a "defined_in" tag to each resource pack's properties unless `add_defined_in` is False.'''
    output:defaultdict[str,dict[str,a]] = defaultdict(empty_dict_lambda)
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string].update(data[resource_pack])
            if add_defined_in:
                defined_in_key = output[tag_string].get("defined_in")
                if defined_in_key is None:
                    output[tag_string]["defined_in"] = [resource_pack]
                else:
                    defined_in_key.append(resource_pack)
    # aaaa = type(data)(output)
    # print(type(aaaa))
    # return aaaa
    return type(data)(output)

def collapse_resource_packs_flat(data:dict[str,a]) -> dict[str,a]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.'''
    output:dict[str,a] = {}
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string] = data[resource_pack]
    return output

def collapse_resource_pack_names(data:list[str]) -> list[str]:
    output:list[str] = []
    exists_in_output:set[int] = set() # set of IDs because values of resource_pack_tag_strings are always the same.
    for properties_resource_pack in data:
        tag_str = resource_pack_tag_strings.get(properties_resource_pack)
        if tag_str is None:
            raise Exceptions.UnrecognizedPackError(properties_resource_pack, "pack")
        if (tag_str_id := id(tag_str)) not in exists_in_output:
            exists_in_output.add(tag_str_id)
            output.append(tag_str)
    return list(reversed(output)) # reversed so it behaves the same as it does before refactor.
