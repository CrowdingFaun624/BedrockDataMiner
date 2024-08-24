from typing import Any, TypedDict

import Utilities.File as File

__all__ = ["item_textures_normalize"]

item_textures_data_typed_dict = TypedDict("item_textures_data_typed_dict", texture_data=dict[str,Any])

def item_textures_normalize(data:dict[str,File.File[item_textures_data_typed_dict]]) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = {}
    for resource_pack_name, item_textures_file in data.items():
        item_textures_data = item_textures_file.read()
        for item, item_data in item_textures_data["texture_data"].items():
            if item not in output:
                output[item] = {}
            output[item][resource_pack_name] = item_data
    return output
