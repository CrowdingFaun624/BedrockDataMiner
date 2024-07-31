from typing import Any, TypedDict, cast

__all__ = ["entities_client_fix_old"]

input_description_typed_dict = TypedDict("input_description_typed_dict", {
    "animation_controllers": Any,
    "animations": Any,
    "enable_attachables": Any,
    "geometry": Any,
    "held_item_ignores_lighting": Any,
    "hide_armor": Any,
    "identifier": Any,
    "locators": Any,
    "materials": Any,
    "min_engine_version": Any,
    "particle_effects": Any,
    "particle_emitters": Any,
    "render_controllers": Any,
    "scripts": Any,
    "sound_effects": Any,
    "spawn_egg": Any,
    "textures": Any,
})

input_type = dict[str,input_description_typed_dict]

output_description_typed_dict = TypedDict("output_description_typed_dict", {
    "animation_controllers": Any,
    "animations": Any,
    "enable_attachables": Any,
    "geometry": Any,
    "held_item_ignores_lighting": Any,
    "hide_armor": Any,
    "identifier": Any,
    "locators": Any,
    "materials": Any,
    "min_engine_version": Any,
    "particle_effects": Any,
    "particle_emitters": Any,
    "render_controllers": Any,
    "scripts": Any,
    "sound_effects": Any,
    "spawn_egg": Any,
    "textures": Any,
})

output_client_entity_typed_dict = TypedDict("output_client_entity_typed_dict", {
    "description": output_description_typed_dict,
})

output_type = TypedDict("output_type", {
    "defined_in": list[str],
    "minecraft:client_entity": output_client_entity_typed_dict,
})

def entities_client_fix_old(data:input_type|output_type) -> output_type|None:
    if "minecraft:client_entity" in data:
        return None
    client_entity_identifier = list(data.keys())[0]
    output:output_type = {
        "defined_in": cast(list[str], data["defined_in"]),
        "minecraft:client_entity": {
            "description": data[client_entity_identifier]
        }
    }
    return output
