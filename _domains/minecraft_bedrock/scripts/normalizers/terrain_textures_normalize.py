from typing import Any

import Utilities.File as File

__all__ = ["terrain_textures_normalize"]

def terrain_textures_normalize(data:dict[str,File.File[dict[str,Any]]]) -> File.FakeFile[dict[str,dict[str,Any]]]:
    other_keys = {"texture_name": {}, "padding": {}, "num_mip_levels": {}}
    texture_data:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for resource_pack_name, terrain_textures_file in data.items():
        terrain_textures_data = terrain_textures_file.data
        file_hashes.append(hash(terrain_textures_file))
        for other_key_key, other_key_values in other_keys.items():
            if other_key_key in terrain_textures_data:
                other_key_values[resource_pack_name] = terrain_textures_data[other_key_key]
        for terrain, terrain_data in terrain_textures_data["texture_data"].items():
            if terrain not in texture_data:
                texture_data[terrain] = {}
            texture_data[terrain][resource_pack_name] = terrain_data
    output = other_keys
    output["texture_data"] = texture_data
    return File.FakeFile("combined_terrain_textures_file", output, hash(tuple(file_hashes)))
