from collections import defaultdict
from typing import TypeVar

import _assets.scripts.normalizers.collapse_resource_packs.util as util
import Utilities.File as File

a = TypeVar("a")

__all__ = ["collapse_resource_packs_dict"]

def collapse_resource_packs_dict(data:dict[str,File.AbstractFile[dict[str,a]]], add_defined_in:bool=True) -> File.FakeFile[dict[str,dict[str,a]]]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    Also adds a "defined_in" tag to each resource pack's properties unless `add_defined_in` is False.'''
    output:defaultdict[str,dict[str,a]] = defaultdict(lambda: {})
    file_hashes:list[int] = []
    for tag_string, resource_pack_list in util.get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: util.resource_pack_order[item])
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
