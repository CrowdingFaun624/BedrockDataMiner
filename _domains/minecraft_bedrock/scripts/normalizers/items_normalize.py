from typing import Any, Iterator, TypedDict, cast

from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import Serializer
from Utilities.File import AbstractFile, FakeFile, File

domain = get_domain_from_module(__name__)
json_serializer = domain.script_referenceable.get_future("minecraft_common!serializers/json", Serializer)

class ItemsFileFormat(TypedDict):
    items: dict[str,dict[str,Any]]

type OldType = dict[str,File[ItemsFileFormat|list[dict[str,str]]]]

type NewType = dict[str,dict[str,File[Any]]]

def is_old_format(data:OldType|NewType) -> bool:
    return isinstance(list(data.values())[0], AbstractFile)

def iterator_old(data:OldType) -> Iterator[tuple[str,str,Any, int]]:
    for resource_pack_name, file in data.items():
        items = file.read(json_serializer.get())
        if isinstance(items, dict):
            for item_name, item in items["items"].items():
                yield item_name, resource_pack_name, item, hash(file)
        else:
            for item in items:
                yield item.pop("name"), resource_pack_name, item, hash(file)

def iterator_new(data:NewType) -> Iterator[tuple[str,str,Any,int]]:
    for item_file_name, resource_packs in data.items():
        item_name = item_file_name.removesuffix(".json")
        for resource_pack_name, file in resource_packs.items():
            yield item_name, resource_pack_name, file.read(json_serializer.get()), hash(file)

@component_function(no_arguments=True)
def items_normalize(data:OldType|NewType) -> FakeFile[dict[str,dict[str,Any]]]:
    iterator:Iterator[tuple[str,str,Any,int]] = iterator_old(cast(OldType, data)) if is_old_format(data) else iterator_new(cast(NewType, data))
    # item name, resource pack, item data; return is file hashes
    output:dict[str,dict[str,Any]] = {}
    file_hashes_set:set[int] = set()
    file_hashes:list[int] = []
    for item_name, resource_pack_name, item_data, file_hash in iterator:
        if file_hash not in file_hashes_set:
            file_hashes.append(file_hash)
            file_hashes_set.add(file_hash)
        if item_name not in output:
            output[item_name] = {}
        output[item_name][resource_pack_name] = item_data
    return FakeFile("combined_items_file", output, None, hash(tuple(file_hashes)))
