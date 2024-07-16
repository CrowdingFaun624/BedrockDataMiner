import json
from collections import defaultdict
from typing import Any, Callable, TypedDict

import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Utilities.Nbt.NbtTypes as NbtTypes


def delete_required_key(data:dict[str,Any], key:str) -> None:
    del data[key]

def delete_optional_key(data:dict[str,Any], key:str) -> None:
    data.pop(key, None)

def delete_required_keys(data:dict[str,Any], keys:list[str]) -> None:
    for key in keys:
        del data[key]

def delete_optional_keys(data:dict[str,Any], keys:list[str]) -> None:
    for key in keys:
        data.pop(key, None)

def load_json(data:NbtTypes.TAG_String) -> dict[str,str]:
    return json.loads(data.value)

def wrap_in_dict(data:list[dict[str,Any]], key:str, delete:bool=False) -> dict[str,dict[str,Any]]:
    output = {item[key]: item for item in data}
    if delete:
        for value in output.values():
            del value[key]
    return output

def wrap_tuple(data:list[Any], keys:list[str]) -> dict[str,Any]:
    assert len(data) == len(keys)
    return {key: value for key, value in zip(keys, data)}

def animation_controllers_fix_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "animation_controllers" in data: return
    defined_in = data["defined_in"]
    output = {"defined_in": defined_in, "animation_controllers": data}
    del output["animation_controllers"]["defined_in"]
    return output

def animations_fix_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "animations" in data: return
    defined_in = data["defined_in"]
    output = {"defined_in": defined_in, "animations": data}
    del output["animations"]["defined_in"]
    return output

def attachables_normalize_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "minecraft:attachable" in data: return
    attachable_identifier = list(data.keys())[0]
    output = {"minecraft:attachable": {"description": data[attachable_identifier]}}
    output["minecraft:attachable"]["description"]["identifier"] = attachable_identifier
    return output

def behavior_packs_normalize(data:DataMinerTyping.BehaviorPacks) -> list[str]:
    return [behavior_pack["name"] for behavior_pack in data]

def biomes_normalize_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "minecraft:biome" in data: return
    biome_name = list(data.keys())[0]
    format_version:str = data[biome_name]["format_version"]
    output = {"format_version": format_version, "minecraft:biome": {"components": data[biome_name], "description": {"identifier": biome_name}}}
    del output["minecraft:biome"]["components"]["format_version"]
    return output

def blocks_client_normalize(data:DataMinerTyping.MyBlocksClient) -> dict[str,dict[str,DataMinerTyping.BlocksJsonClientBlockTypedDict]]:
    return {block["name"]: block["properties"] for block in data}

def entities_client_fix_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "minecraft:client_entity" in data: return
    defined_in = data["defined_in"]
    entity_client_name = list(data.keys())[0]
    return {"defined_in": defined_in, "minecraft:client_entity": {"description": data[entity_client_name]}}

def item_textures_normalize(data:dict[str,dict[str,dict[str,dict[str,str]]]]) -> dict[str,Any]:
    output:dict[str,dict[str,Any]] = {}
    for resource_pack_name, item_textures_data in data.items():
        for item, item_data in item_textures_data["texture_data"].items():
            if item in output:
                output[item][resource_pack_name] = item_data
            else:
                output[item] = {resource_pack_name: item_data}
    return output

recipes_fix_old_data = {
        "crafting_shaped": "minecraft:recipe_shaped",
        "crafting_shapeless": "minecraft:recipe_shapeless",
        "furnace_recipe": "minecraft:recipe_furnace",
    }
def recipes_fix_old(data:dict[str,Any]) -> dict[str,dict[str,Any]]|None:
    if "type" not in data: return None
    old_recipe_type = data["type"]
    del data["type"]
    del data["defined_in"]
    new_recipe_type = recipes_fix_old_data.get(old_recipe_type)
    if new_recipe_type is None:
        raise KeyError("Recipe type \"%s\" not recognized!" % old_recipe_type)
    return {new_recipe_type: data}

def languages_normalize_fix_properties(data:DataMinerTyping.LanguagesTypedDict) -> dict[str,Any]:
    output:dict[str,DataMinerTyping.LanguagesPropertiesTypedDict] = data["properties"]
    for resource_pack in data["defined_in"]:
        if resource_pack not in output:
            output[resource_pack] = {}
    return output

def languages_normalize(data:DataMinerTyping.Languages) -> DataMinerTyping.NormalizedLanguages:
    return {language["code"]: languages_normalize_fix_properties(language) for language in data}

def materials_normalize_material(data:dict[str,dict[str,Any]]) -> dict[str,dict[str,Any]]|None:
    if "materials" in data:
        data["version"] = data["materials"]["version"]
    else:
        return {"materials": data, "defined_in": data["defined_in"]}

def models_model_normalize(data:dict[str,dict[str,dict[str,Any]]]) -> dict[str,Any]:
    output:defaultdict[str,dict[str,Any]] = defaultdict(lambda: {})
    for model_file_name, resource_packs in data.items():
        for resource_pack_name, model_file_data in resource_packs.items():
            if "minecraft:geometry" in model_file_data:
                format_version:str|None = model_file_data["format_version"]
                assert isinstance(model_file_data["minecraft:geometry"], list)
                for geometry_item in model_file_data["minecraft:geometry"]:
                    name = geometry_item["description"]["identifier"]
                    model_output_name = "%s %s" % (model_file_name, name)
                    if resource_pack_name in output[model_output_name]:
                        raise KeyError("Multiple models using name \"%s\" and resource pack \"%s\"!" % (model_output_name, resource_pack_name))
                    output[model_output_name][resource_pack_name] = {"format_version": format_version, "minecraft:geometry": geometry_item}
            else:
                format_version:str|None = model_file_data["format_version"] if "format_version" in model_file_data else None
                for name, model_data in model_file_data.items():
                    if name == "format_version": continue
                    description_dict = {"identifier": name}
                    model_output_name = "%s %s" % (model_file_name, name)
                    for description_key in list(model_data.keys()):
                        if description_key in ("bones",): continue
                        description_dict[description_key] = model_data[description_key]
                        del model_data[description_key]
                    model_data["description"] = description_dict
                    if resource_pack_name in output[model_output_name]:
                        raise KeyError("Multiple models using name \"%s\" and resource pack \"%s\"!" % (model_output_name, resource_pack_name))
                    output[model_output_name][resource_pack_name] = {"format_version": format_version, "minecraft:geometry": model_data}
    return dict(output)

is_valid_color:Callable[[Any],bool] = lambda color: (isinstance(color, list) and len(color) in (3, 4) and all(isinstance(channel, (int, float, str)) for channel in color)) or isinstance(color, str)
def particles_normalize_component_particle_appearance_tinting_color(data:str|list[int]|dict[str,str|list[int]]|list[str|list[int]]) -> list|None:
    if is_valid_color(data):
        return [data]

def particles_normalize_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "particles" not in data:
        return
    assert len(data["particles"]) == 1
    particle_identifier:str = list(data["particles"].keys())[0]
    output = {"format_version": data["format_version"], "defined_in": data["defined_in"], "particle_effect": data["particles"][particle_identifier]}
    output["particle_effect"]["description"] = {"basic_render_parameters": data["particles"][particle_identifier]["basic_render_parameters"], "identifier": particle_identifier}
    del output["particle_effect"]["basic_render_parameters"]
    return output

def resource_packs_normalize(data:DataMinerTyping.ResourcePacks) -> list[str]:
    return [resource_pack["name"] for resource_pack in data]

def render_controllers_fix_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "render_controllers" in data: return
    defined_in = data["defined_in"]
    del data["defined_in"]
    return {"defined_in": defined_in, "render_controllers": data}

def renderer_platform_configuration_normalize_shadow_config(data:dict[str,str]) -> dict[str,dict[str,str]]|None:
    if "file" in data:
        return {"shadow_config": data}

def sound_definitions_make_strings_to_dict(data:str|DataMinerTyping.SoundDefinitionsJsonSoundTypedDict) -> DataMinerTyping.SoundDefinitionsJsonSoundTypedDict|None:
    if isinstance(data, str):
        return {"name": data}

def sounds_json_remove_bad_events(data:dict[str,str|DataMinerTyping.SoundsJsonSoundTypedDict]) -> None:
    events_to_delete:list[str] = []
    for event_name, event_properties in data.items():
        if isinstance(event_properties, str): continue
        if "sound" not in event_properties and "sounds" not in event_properties:
            events_to_delete.append(event_name)
    for event_to_delete in events_to_delete:
        del data[event_to_delete]

def sounds_json_remove_bad_interactive_entity_events(data:dict[str,dict[str,str]]) -> None:
    events_to_delete:list[str] = []
    for event_name, event_properties in data.items():
        if isinstance(event_properties, str): continue
        if "default" not in event_properties:
            events_to_delete.append(event_name)
    for event_to_delete in events_to_delete:
        del data[event_to_delete]

def sounds_json_fix_sounds(data:DataMinerTyping.SoundsJsonSoundTypedDict) -> None:
    '''moves key "sounds" to "sound". It occurs a whole lot and for a long time, so it's gotta be on purpose.'''
    # TODO: find out if "sounds" is actually a valid key.
    if "sounds" in data:
        data["sound"] = data["sounds"]
        del data["sounds"]

def spawn_rules_normalize_herd(data:dict[str,Any]|list[dict[str,Any]]) -> list[dict[str,Any]]|None:
    if isinstance(data, dict):
        return [data]

terrain_textures_normalize_typed_dict = TypedDict("terrain_textures_normalize_typed_dict", {"resource_pack_name": str, "texture_name": str, "padding": int, "num_mip_levels": int, "texture_data": dict[str,dict[str,str]]})
def terrain_textures_normalize(data:dict[str,terrain_textures_normalize_typed_dict]) -> dict[str,Any]:
    normal_keys = set(["resource_pack_name", "texture_name", "padding", "num_mip_levels", "texture_data"])
    other_keys = {"texture_name": {}, "padding": {}, "num_mip_levels": {}}
    texture_data:defaultdict[str,dict[str,Any]] = defaultdict(lambda: {})
    for resource_pack_name, terrain_textures_data in data.items():
        assert set(terrain_textures_data.keys()) == normal_keys
        for other_key_key, other_key_values in other_keys.items():
            if other_key_key in terrain_textures_data:
                other_key_values[resource_pack_name] = terrain_textures_data[other_key_key]
        for terrain, terrain_data in terrain_textures_data["texture_data"].items():
            texture_data[terrain][resource_pack_name] = terrain_data
    output = other_keys
    output["texture_data"] = dict(texture_data)
    return output

def texture_list_normalize(data:dict[str,list[str]]) -> dict[str,list[str]]:
    output:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack, textures in data.items():
        for texture in textures:
            output[texture].append(resource_pack)
    return dict(output)

functions:dict[str,Callable] = {
    "delete_required_key": delete_required_key,
    "delete_optional_key": delete_optional_key,
    "delete_required_keys": delete_required_keys,
    "delete_optional_keys": delete_optional_keys,
    "load_json": load_json,
    "wrap_in_dict": wrap_in_dict,
    "wrap_tuple": wrap_tuple,
    "collapse_resource_pack_names": CollapseResourcePacks.collapse_resource_pack_names,
    "collapse_resource_packs_dict": CollapseResourcePacks.collapse_resource_packs_dict,
    "collapse_resource_packs_list": CollapseResourcePacks.collapse_resource_packs_list,
    "collapse_resource_packs_flat": CollapseResourcePacks.collapse_resource_packs_flat,
    "animation_controllers_fix_old": animation_controllers_fix_old,
    "animations_fix_old": animations_fix_old,
    "attachables_normalize_old": attachables_normalize_old,
    "behavior_packs_normalize": behavior_packs_normalize,
    "biomes_normalize_old": biomes_normalize_old,
    "blocks_client_normalize": blocks_client_normalize,
    "entities_client_fix_old": entities_client_fix_old,
    "item_textures_normalize": item_textures_normalize,
    "recipes_fix_old": recipes_fix_old,
    "languages_normalize": languages_normalize,
    "materials_normalize_material": materials_normalize_material,
    "models_model_normalize": models_model_normalize,
    "particles_normalize_component_particle_appearance_tinting_color": particles_normalize_component_particle_appearance_tinting_color,
    "particles_normalize_old": particles_normalize_old,
    "resource_packs_normalize": resource_packs_normalize,
    "render_controllers_fix_old": render_controllers_fix_old,
    "renderer_platform_configuration_normalize_shadow_config": renderer_platform_configuration_normalize_shadow_config,
    "sound_definitions_make_strings_to_dict": sound_definitions_make_strings_to_dict,
    "sounds_json_remove_bad_events": sounds_json_remove_bad_events,
    "sounds_json_remove_bad_interactive_entity_events": sounds_json_remove_bad_interactive_entity_events,
    "sounds_json_fix_sounds": sounds_json_fix_sounds,
    "spawn_rules_normalize_herd": spawn_rules_normalize_herd,
    "terrain_textures_normalize": terrain_textures_normalize,
    "texture_list_normalize": texture_list_normalize,
}
