from collections import defaultdict

import Utilities.File as File

__all__ = ["texture_list_normalize"]

def texture_list_normalize(data:dict[str,File.File[list[str]]]) -> dict[str,list[str]]:
    output:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack, textures_file in data.items():
        textures = textures_file.read()
        for texture in textures:
            output[texture].append(resource_pack)
    return dict(output)
