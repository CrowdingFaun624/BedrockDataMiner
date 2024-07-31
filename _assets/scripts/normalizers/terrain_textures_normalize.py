from typing import Any

__all__ = ["terrain_textures_normalize"]

def terrain_textures_normalize(data:Any) -> Any:
    other_keys = {"texture_name": {}, "padding": {}, "num_mip_levels": {}}
    texture_data:dict[str,dict[str,Any]] = {}
    for resource_pack_name, terrain_textures_data in data.items():
        for other_key_key, other_key_values in other_keys.items():
            if other_key_key in terrain_textures_data:
                other_key_values[resource_pack_name] = terrain_textures_data[other_key_key]
        for terrain, terrain_data in terrain_textures_data["texture_data"].items():
            if terrain not in texture_data:
                texture_data[terrain] = {}
            texture_data[terrain][resource_pack_name] = terrain_data
    output = other_keys
    output["texture_data"] = texture_data
    return output
