from collections import defaultdict

import Utilities.File as File

__all__ = ["texture_list_normalize"]

def texture_list_normalize(data:dict[str,File.File[list[str]]]) -> File.FakeFile[dict[str,list[str]]]:
    output:defaultdict[str,list[str]] = defaultdict(lambda: [])
    file_hashes:list[int] = []
    for resource_pack, textures_file in data.items():
        textures = textures_file.data
        file_hashes.append(hash(textures_file))
        for texture in textures:
            output[texture].append(resource_pack)
    return File.FakeFile("combined_texture_list_file", dict(output), hash(tuple(file_hashes)))
