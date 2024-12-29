from typing import Any, TypedDict

__all__ = ["biomes_normalize_old"]

input_biome_typed_dict = TypedDict("input_biome_typed_dict", {
    "format_version": str,
})

input_typed_dict = dict[str,input_biome_typed_dict]

output_description_typed_dict = TypedDict("output_description_typed_dict", {
    "identifier": str,
})

output_biome_typed_dict = TypedDict("output_biome_typed_dict", {
    "components": Any,
    "description": output_description_typed_dict,
})

output_typed_dict = TypedDict("output_typed_dict", {
    "format_version": str,
    "minecraft:biome": output_biome_typed_dict,
})

def biomes_normalize_old(data:input_typed_dict|output_typed_dict) -> output_typed_dict|None:
    if "minecraft:biome" in data:
        return None
    biome_identifier = list(data.keys())[0]
    output:output_typed_dict = {
        "format_version": data[biome_identifier]["format_version"],
        "minecraft:biome": {
            "components": data[biome_identifier],
            "description": {
                "identifier": biome_identifier
            }
        }
    }
    del output["minecraft:biome"]["components"]["format_version"]
    return output
