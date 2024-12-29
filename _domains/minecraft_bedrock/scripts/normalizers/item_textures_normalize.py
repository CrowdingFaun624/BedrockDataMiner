from typing import Any, TypedDict

import Utilities.File as File

__all__ = ["item_textures_normalize"]

item_textures_data_typed_dict = TypedDict("item_textures_data_typed_dict", {"texture_data": dict[str,Any]})

def item_textures_normalize(data:dict[str,File.File[item_textures_data_typed_dict]]) -> File.FakeFile[dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for resource_pack_name, item_textures_file in data.items():
        file_hashes.append(hash(item_textures_file))
        item_textures_data = item_textures_file.data
        for item, item_data in item_textures_data["texture_data"].items():
            if item not in output:
                output[item] = {}
            output[item][resource_pack_name] = item_data
    return File.FakeFile("combined_item_textures_file", output, hash(tuple(file_hashes)))
