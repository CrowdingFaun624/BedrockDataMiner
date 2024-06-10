import enum
import json
from typing import TYPE_CHECKING, Any, Callable, TypedDict, TypeVar, cast

import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import DataMiner.DataMinerTyping as DataMinerTyping

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

resource_pack_data = get_resource_pack_order()
resource_pack_order = {resource_pack["name"]: index for index, resource_pack in enumerate(resource_pack_data)}
resource_pack_dict = {resource_pack_name: resource_pack for resource_pack_name, resource_pack in zip(resource_pack_order, resource_pack_data)}

a = TypeVar("a")

def make_interface(has_defined_in_key:bool=True, extend:bool=True) -> Callable[[dict[str,Any],"DataMinerTyping.DependenciesTypedDict"],None]:
    def collapse_resource_packs_interface(data:dict[str,Any], dependencies:"DataMinerTyping.DependenciesTypedDict") -> None:
        collapse_resource_packs(data, has_defined_in_key, extend)
    return collapse_resource_packs_interface

def collapse_resource_packs(data:dict[str,a], add_defined_in:bool=True, extend:bool=True) -> dict[str,a]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    Also adds a "defined_in" tag to each resource pack's properties unless `add_defined_in` is False.'''
    resource_packs_by_tag:dict[str,list[str]] = {}
    for resource_pack in data.keys():
        if resource_pack not in resource_pack_order:
            raise Exceptions.UnrecognizedPackError(resource_pack, "pack")
        tag_string = ",".join(resource_pack_dict[resource_pack]["tags"])
        if tag_string in resource_packs_by_tag:
            resource_packs_by_tag[tag_string].append(resource_pack)
        else:
            resource_packs_by_tag[tag_string] = [resource_pack]
    output:dict[str,a] = {}
    for tag_string, resource_pack_list in resource_packs_by_tag.items():
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            data_item = data[resource_pack]
            if extend and isinstance(data_item, dict):
                if tag_string in output:
                    output[tag_string].update(data_item)
                else:
                    output[tag_string] = data_item
            elif extend and isinstance(data_item, list):
                if tag_string in output:
                    output[tag_string].extend(data_item)
                else:
                    output[tag_string] = data_item
            else:
                output[tag_string] = data_item
            if add_defined_in:
                defined_in_key = cast(list[str]|None, cast(dict, output[tag_string]).get("defined_in", None))
                if defined_in_key is None:
                    output[tag_string]["defined_in"] = [resource_pack] # type:ignore
                else:
                    defined_in_key.append(resource_pack)
    data.clear()
    data.update(output)
    return data

def collapse_resource_pack_list(data:list[str], dependencies:"DataMinerTyping.DependenciesTypedDict") -> list[str]:
    for properties_resource_pack in data:
        if properties_resource_pack not in resource_pack_dict:
            raise Exceptions.UnrecognizedPackError(properties_resource_pack, "pack")
    output:list[str] = []
    exists_in_output:set[str] = set()
    while len(data) > 0:
        properties_resource_pack = data.pop()
        if properties_resource_pack not in resource_pack_dict:
            raise Exceptions.UnrecognizedPackError(properties_resource_pack, "pack")
        tags_str = ",".join(resource_pack_dict[properties_resource_pack]["tags"])
        if tags_str not in exists_in_output:
            output.append(tags_str)
            exists_in_output.add(tags_str)
    for item in output:
        data.append(item)
    return data
