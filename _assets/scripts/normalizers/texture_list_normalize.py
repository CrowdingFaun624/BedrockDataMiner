from collections import defaultdict

__all__ = ["texture_list_normalize"]

def texture_list_normalize(data:dict[str,list[str]]) -> dict[str,list[str]]:
    output:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack, textures in data.items():
        for texture in textures:
            output[texture].append(resource_pack)
    return dict(output)
