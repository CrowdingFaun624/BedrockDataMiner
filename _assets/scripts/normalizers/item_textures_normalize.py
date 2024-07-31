from typing import Any, TypedDict

__all__ = ["item_textures_normalize"]

item_textures_data_typed_dict = TypedDict("item_textures_data_typed_dict", texture_data=dict[str,Any])

def item_textures_normalize(data:dict[str,item_textures_data_typed_dict]) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = {}
    for resource_pack_name, item_textures_data in data.items():
        for item, item_data in item_textures_data["texture_data"].items():
            if item not in output:
                output[item] = {}
            output[item][resource_pack_name] = item_data
    return output
