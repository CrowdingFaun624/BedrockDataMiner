from collections import defaultdict
from typing import Any, NotRequired, Required, TypedDict, cast

import Utilities.File as File

__all__ = [
    "animation_controllers_fix_old",
    "animations_fix_old",
    "attachables_normalize_old",
    "biomes_normalize_old",
    "blocks_client_normalize",
    "categories_normalize",
    "commands_normalize_format_string",
    "entities_client_fix_old",
    "item_textures_normalize",
    "items_client_offset_normalize",
    "language_names_normalize",
    "materials_normalize_material",
    "music_definitions_normalize",
    "normalize_sound_definitions",
    "packs_normalize",
    "particles_normalize_component_particle_appearance_tinting_color",
    "particles_normalize_old",
    "recipes_fix_old",
    "remove_minecraft_prefix",
    "render_controllers_fix_old",
    "renderer_options_dragon_normalize",
    "renderer_options_normalize_mappings",
    "renderer_platform_configurations_normalize_shadow_config",
    "skins_normalize",
    "sound_definitions_make_strings_to_dict",
    "sounds_json_make_strings_to_dict",
    "spawn_rules_normalize_herd",
    "terrain_textures_normalize",
    "texture_list_normalize",
    "ui_separate_variables",
    "uniforms_normalize",
]

animation_controllers_fix_old_input_typed_dict = dict[str,Any]
animation_controllers_fix_old_output_typed_dict = TypedDict("animation_controllers_fix_old_output_typed_dict", {"animation_controllers": Any})

def animation_controllers_fix_old(data:animation_controllers_fix_old_input_typed_dict|animation_controllers_fix_old_output_typed_dict) -> animation_controllers_fix_old_output_typed_dict|None:
    if "animation_controllers" in data:
        return None
    output:animation_controllers_fix_old_output_typed_dict = {"animation_controllers": data}
    return output

animations_fix_old_input_typed_dict = dict[str,Any]
animations_fix_old_output_typed_dict = TypedDict("animations_fix_old_output_typed_dict", {"animations": Any})

def animations_fix_old(data:animations_fix_old_input_typed_dict|animations_fix_old_output_typed_dict) -> animations_fix_old_output_typed_dict|None:
    if "animations" in data:
        return None
    output:animations_fix_old_output_typed_dict = {"animations": data}
    return output

attachables_normalize_old_input_description_typed_dict = TypedDict("attachables_normalize_old_input_description_typed_dict", {
    "item": Any,
    "animations": Any,
    "geometry": Any,
    "materials": Any,
    "render_controllers": Any,
    "scripts": Any,
    "textures": Any,
})

attachables_normalize_old_input_typed_dict = dict[str,attachables_normalize_old_input_description_typed_dict]

attachables_normalize_old_output_description_typed_dict = TypedDict("attachables_normalize_old_output_description_typed_dict", {
    "identifier": NotRequired[str],
    "item": Any,
    "animations": Any,
    "geometry": Any,
    "materials": Any,
    "render_controllers": Any,
    "scripts": Any,
    "textures": Any,
})

attachables_normalize_old_output_attachable_typed_dict = TypedDict("attachables_normalize_old_output_attachable_typed_dict", {"description": attachables_normalize_old_output_description_typed_dict})

attachables_normalize_old_output_typed_dict = TypedDict("attachables_normalize_old_output_typed_dict", {"minecraft:attachable": attachables_normalize_old_output_attachable_typed_dict})

def attachables_normalize_old(data:attachables_normalize_old_input_typed_dict|attachables_normalize_old_output_typed_dict) -> attachables_normalize_old_output_typed_dict|None:
    if "minecraft:attachable" in data:
        return None
    attachable_identifier = list(data.keys())[0]
    output:attachables_normalize_old_output_typed_dict = {"minecraft:attachable": {"description": data[attachable_identifier]}} # type: ignore
    output["minecraft:attachable"]["description"]["identifier"] = attachable_identifier
    return output

biomes_normalize_old_input_biome_typed_dict = TypedDict("biomes_normalize_old_input_biome_typed_dict", {
    "format_version": str,
})

biomes_normalize_old_input_typed_dict = dict[str,biomes_normalize_old_input_biome_typed_dict]

biomes_normalize_old_output_description_typed_dict = TypedDict("biomes_normalize_old_output_description_typed_dict", {
    "identifier": str,
})

biomes_normalize_old_output_biome_typed_dict = TypedDict("biomes_normalize_old_output_biome_typed_dict", {
    "components": Any,
    "description": biomes_normalize_old_output_description_typed_dict,
})

biomes_normalize_old_output_typed_dict = TypedDict("biomes_normalize_old_output_typed_dict", {
    "format_version": str,
    "minecraft:biome": biomes_normalize_old_output_biome_typed_dict,
})

def biomes_normalize_old(data:biomes_normalize_old_input_typed_dict|biomes_normalize_old_output_typed_dict) -> biomes_normalize_old_output_typed_dict|None:
    if "minecraft:biome" in data:
        return None
    biome_identifier = list(data.keys())[0]
    output:biomes_normalize_old_output_typed_dict = {
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

def blocks_client_normalize(data:dict[str,File.File[dict[str,Any]]]) -> File.FakeFile[dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, blocks in data.items():
        file_hashes.append(blocks.hash)
        for block_name, block_data in blocks.data.items():
            if block_name == "format_version": continue
            if block_name not in output:
                output[block_name] = {}
            output[block_name][pack_name] = block_data
    combined_hash = hash(tuple(file_hashes))
    return File.FakeFile("combined_blocks_file", output, combined_hash)

def categories_normalize(data:dict[str,dict[str,str]]) -> dict[str,dict[str,dict[str,str]]]:
    output:dict[str,dict[str,dict[str,str]]] = {}
    for element_name, element in data.items():
        output[element_name] = {element["type"]: element}
    return output

class FormatStringTypedDict(TypedDict):
    format: Required[str]
    color: NotRequired[str]
    should_show: NotRequired[dict[Any,Any]]
    params_to_use: NotRequired[list[Any]]

def commands_normalize_format_string(data:str|FormatStringTypedDict) -> FormatStringTypedDict|None:
    if isinstance(data, dict):
        return None
    else:
        return {"format": data}

entities_client_fix_old_input_type = dict[str,Any]

entities_client_fix_old_output_client_entity_typed_dict = TypedDict("entities_client_fix_old_output_client_entity_typed_dict", {
    "description": Any,
})

entities_client_fix_old_output_type = TypedDict("entities_client_fix_old_output_type", {
    "minecraft:client_entity": entities_client_fix_old_output_client_entity_typed_dict,
})

def entities_client_fix_old(data:entities_client_fix_old_input_type|entities_client_fix_old_output_type) -> entities_client_fix_old_output_type|None:
    if "minecraft:client_entity" in data:
        return None
    client_entity_identifier = list(data.keys())[0]
    output:entities_client_fix_old_output_type = {
        "minecraft:client_entity": {
            "description": data[client_entity_identifier]
        }
    }
    return output

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

class ItemClientOffsetItemTypedDict(TypedDict):
    VR_hand_controller_position_adjust: Required[list[float]]
    VR_hand_controller_rotation_adjust: Required[list[float]]
    VR_hand_controller_scale: Required[float]

class ItemClientOffsetFileTypedDict(TypedDict):
    render_offsets: Required[dict[str,ItemClientOffsetItemTypedDict]]

def items_client_offset_normalize(data:dict[str,File.File[ItemClientOffsetFileTypedDict]]) -> File.FakeFile[dict[str,dict[str,ItemClientOffsetItemTypedDict]]]:
    output:dict[str,dict[str,ItemClientOffsetItemTypedDict]] = {}
    file_hashes:list[int] = []
    for resource_pack_name, file in data.items():
        file_data = file.data
        file_hashes.append(hash(file))
        output[resource_pack_name] = file_data["render_offsets"]
    return File.FakeFile("combined_items_client_offset_file", output, hash(tuple(file_hashes)))

def language_names_normalize(data:list[list[str]]) -> dict[str,str]:
    return dict(data)

materials_normalize_material_input_typed_dict = TypedDict("materials_normalize_material_input_typed_dict", {"version": str, "materials": dict[str,Any]})

materials_normalize_material_output_typed_dict = TypedDict("materials_normalize_material_output_typed_dict", {"materials": dict[str,Any]})

def materials_normalize_material(data:materials_normalize_material_input_typed_dict|dict[str,Any]) -> materials_normalize_material_output_typed_dict|None:
    if "materials" in data:
        data["version"] = cast(str, data["materials"]["version"])
        del data["materials"]["version"]
    else:
        return {"materials": data}

def music_definitions_normalize(data:dict[str,File.File[dict[str,Any]]]) -> File.FakeFile[dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, music_definitions_file in data.items():
        music_definitions = music_definitions_file.data
        file_hashes.append(hash(music_definitions_file))
        for environment_name, environment_data in music_definitions.items():
            if environment_name not in output:
                output[environment_name] = {}
            output[environment_name][pack_name] = environment_data
    return File.FakeFile("combined_music_definitions_file", output, hash(tuple(file_hashes)))

def normalize_sound_definitions(data:dict[str,File.File[dict[str,Any]]]) -> File.FakeFile[dict[str,dict[str,Any]]]:
    # resource packs are always the top level.
    # inside resource pack, it's sometimes wrapped in {"sound_definitions": dict_of_sound_events}
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, sound_definitions_file in data.items():
        file_hashes.append(hash(sound_definitions_file))
        sound_definitions = sound_definitions_file.data
        if "sound_definitions" in sound_definitions:
            sound_definitions:dict[str,Any] = sound_definitions["sound_definitions"]
        for event_name, event_data in sound_definitions.items():
            if event_name not in output:
                output[event_name] = {}
            output[event_name][pack_name] = event_data
    return File.FakeFile("combined_sound_definitions_file", output, hash(tuple(file_hashes)))

packs_normalize_pack_typed_dict = TypedDict("packs_normalize_pack_typed_dict", {"path": str, "name": str})

def packs_normalize(data:list[packs_normalize_pack_typed_dict]) -> list[str]:
    return [pack["name"] for pack in data]

def particles_normalize_component_particle_appearance_tinting_color(data:dict|str|list) -> list|dict|None:
    if isinstance(data, (str, list)):
        return [data]

particles_normalize_old_description_typed_dict = TypedDict("particles_normalize_old_description_typed_dict", {
    "basic_render_parameters": dict[str,Any],
    "identifier": str,
})

particles_normalize_old_particle_effect_typed_dict = TypedDict("particles_normalize_old_particle_effect_typed_dict", {
    "description": particles_normalize_old_description_typed_dict,
})

particles_normalize_old_output_type = TypedDict("particles_normalize_old_output_type", {
    "format_version": str,
    "particle_effect": particles_normalize_old_particle_effect_typed_dict,
})

particles_normalize_old_input_type = dict[str,Any]

def particles_normalize_old(data:particles_normalize_old_input_type|particles_normalize_old_output_type) -> particles_normalize_old_output_type|None:
    if "particles" not in data:
        return
    particle_identifier = list(data["particles"].keys())[0]
    output:particles_normalize_old_output_type = {
        "format_version": cast(str, data["format_version"]),
        "particle_effect": data["particles"][particle_identifier],
    }
    output["particle_effect"]["description"] = {
        "basic_render_parameters": data["particles"][particle_identifier]["basic_render_parameters"],
        "identifier": particle_identifier,
    }
    del output["particle_effect"]["basic_render_parameters"] # type: ignore
    return output

recipes_fix_old_recipe_types = {
    "crafting_shaped": "minecraft:recipe_shaped",
    "crafting_shapeless": "minecraft:recipe_shapeless",
    "furnace_recipe": "minecraft:recipe_furnace",
}

def recipes_fix_old(data:dict[str,Any]) -> dict[str,dict[str,Any]]|None:
    if "type" not in data:
        return None
    new_recipe_type = recipes_fix_old_recipe_types[data["type"]]
    output = {new_recipe_type: data}
    data.pop("defined_in", None)
    del data["type"]
    return output

def remove_minecraft_prefix(data:str) -> str:
    return data.removeprefix("minecraft:")

def render_controllers_fix_old(data:Any) -> Any|None:
    if "render_controllers" in data:
        return None
    output = {"render_controllers": data}
    return output

def renderer_options_dragon_normalize(data:list[list[str]]) -> dict[str,str]:
    return dict(data) # iterable of iterables with two items each

def renderer_options_normalize_mappings(data:dict[str,list[Any]]|list[Any]) -> dict[str,list[Any]]|None:
    if isinstance(data, list):
        return {"mappings": data}

def renderer_platform_configurations_normalize_shadow_config(data:Any) -> Any|None:
    if "file" in data:
        return {"shadow_config": data}

class SkinsNormalizeInputTypedDict(TypedDict):
    skins: list[dict[str,Any]]

class SkinsNormalizeOutputTypedDict(TypedDict):
    skins: list[dict[str,Any]]

def skins_normalize(data:dict[str,File.File[SkinsNormalizeInputTypedDict]], other_keys:list[str]) -> File.FakeFile[SkinsNormalizeOutputTypedDict]:
    output:SkinsNormalizeOutputTypedDict = {
        "skins": [],
    }
    for other_key in other_keys:
        output[other_key] = {}
    file_hashes:list[int] = []
    for pack_name, skins_file in data.items():
        file_hashes.append(hash(skins_file))
        skins_data = skins_file.data
        for skin in skins_data["skins"]:
            skin["defined_in"] = pack_name
            output["skins"].append(skin)
        for other_key in other_keys:
            output[other_key][pack_name] = skins_data[other_key]
    return File.FakeFile("combined_skins_file", output, hash(tuple(file_hashes)))

def sound_definitions_make_strings_to_dict(data:Any) -> Any:
    if isinstance(data, str):
        return {"name": data}

def sounds_json_make_strings_to_dict(data:Any) -> Any:
    if isinstance(data, str):
        return {"sound": data}

def spawn_rules_normalize_herd(data:dict[str,Any]|list[dict[str,Any]]) -> list[dict[str,Any]]|None:
    if isinstance(data, dict):
        return [data]

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

def texture_list_normalize(data:dict[str,File.File[list[str]]]) -> File.FakeFile[dict[str,list[str]]]:
    output:defaultdict[str,list[str]] = defaultdict(lambda: [])
    file_hashes:list[int] = []
    for resource_pack, textures_file in data.items():
        textures = textures_file.data
        file_hashes.append(hash(textures_file))
        for texture in textures:
            output[texture].append(resource_pack)
    return File.FakeFile("combined_texture_list_file", dict(output), hash(tuple(file_hashes)))

def ui_separate_variables(data:dict[str,Any]) -> None:
    variables:dict[str,Any] = {}
    for parameter_name, parameter_value in data.items():
        if parameter_name.startswith("$"):
            variables[parameter_name] = parameter_value
    for variable_name in variables.keys():
        del data[variable_name] # variables are not wanted in the element afterward
    assert "$variables" not in data
    if len(variables) > 0:
        data["$variables"] = variables

def uniforms_normalize(data:dict[str,str]) -> dict[str,str]|None:
    if "Name" in data:
        return
    assert len(data) == 1
    key = list(data.keys())[0]
    value = data[key]
    return {"Name": key, "Type": value}
