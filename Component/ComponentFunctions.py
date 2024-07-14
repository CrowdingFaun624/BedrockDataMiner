import json
from collections import defaultdict
from typing import Any, Callable, TypedDict

import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Utilities.Nbt.NbtTypes as NbtTypes


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

def blocks_client_fix_MCPE_76182(data:DataMinerTyping.BlocksJsonClientBlockTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-76182
    if "sounds" in data:
        del data["sounds"]

def blocks_client_normalize(data:DataMinerTyping.MyBlocksClient) -> dict[str,dict[str,DataMinerTyping.BlocksJsonClientBlockTypedDict]]:
    return {block["name"]: block["properties"] for block in data}

def credits_normalize_sections(data:DataMinerTyping.Credits) -> DataMinerTyping.NormalizedCredits:
    return {section["section"]: section for section in data}

def credits_normalize_disciplines(data:list[DataMinerTyping.CreditsDisciplineTypedDict]) -> dict[str,DataMinerTyping.CreditsDisciplineTypedDict]:
    return {discipline["discipline"]: discipline for discipline in data}

def credits_normalize_titles(data:list[DataMinerTyping.CreditsTitleTypedDict]) -> dict[str,DataMinerTyping.CreditsTitleTypedDict]:
    return {title["title"]: title for title in data}

def entities_fix_event_bug(data:dict[str,Any]) -> None:
    if "minecraft:transformation" in data:
        del data["minecraft:transformation"]

entities_fix_out_of_bounds_components_keys = ["minecraft:physics", "minecraft:pushable", "minecraft:conditional_bandwidth_optimization", "minecraft:raid_persistence"]
def entities_fix_out_of_bounds_components(data:dict[str,Any]) -> None:
    for key_to_delete in entities_fix_out_of_bounds_components_keys:
        if key_to_delete in data:
            del data[key_to_delete]

def entities_fix_MCPE_178417(data:dict[str,Any]) -> None:
    # https://bugs.mojang.com/browse/MCPE-178417
    if len(data) == 0:
        return
    key = list(data.keys())[0]
    if not key.startswith("minecraft:"):
        return
    match key:
        case "minecraft:silverfish_calm":
            del data["minecraft:silverfish_calm"]
        case "minecraft:silverfish_angry":
            del data["minecraft:silverfish_angry"]
        case "minecraft:enderman_calm":
            del data["minecraft:enderman_calm"]
        case "minecraft:enderman_angry":
            del data["minecraft:enderman_angry"]
        case "minecraft:sheep_sheared":
            del data["minecraft:sheep_sheared"]
        case "minecraft:sheep_dyeable":
            del data["minecraft:sheep_dyeable"]

def entities_fix_invalid_components(data:dict[str,Any]) -> None:
    if "minecart:on_hurt_by_player" in data:
        del data["minecart:on_hurt_by_player"]

def entities_fix_priotiry(data:dict[str,Any]) -> None:
    if "priotiry" in data:
        del data["priotiry"]

def entities_client_fix_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "minecraft:client_entity" in data: return
    defined_in = data["defined_in"]
    entity_client_name = list(data.keys())[0]
    return {"defined_in": defined_in, "minecraft:client_entity": {"description": data[entity_client_name]}}

def features_fix_growing_plant_feature_body_blocks(data:list[Any]) -> dict[str,Any]:
    return {"plant_body_block": data[0], "weight": data[1]}

def features_fix_growing_plant_feature_head_blocks(data:list[Any]) -> dict[str,Any]:
    return {"plant_head_block": data[0], "weight": data[1]}

def features_fix_growing_plant_feature_height_distribution(data:list[list[Any]]) -> dict[str,Any]:
    return {"height": data[0], "weight": data[1]}

def features_fix_tree_feature_canopy_leaf_blocks(data:list[Any]) -> dict[str,Any]:
    return {"leaf_blocks": data[0], "weight": data[1]}

def features_fix_weighted_random_features(data:list[Any]) -> dict[str,Any]:
    return {"feature": data[0], "weight": data[1]}

def flipbook_textures_fix_flipbook_textures(data:dict[str,list[dict[str,str]]]) -> None:
    for resource_pack_name, resource_pack_data in data.items():
        start_length = len(resource_pack_data)
        data[resource_pack_name] = {flipbook_texture["atlas_tile"]: flipbook_texture for flipbook_texture in resource_pack_data}
        if len(resource_pack_data) != start_length:
            raise RuntimeError("Duplicate `atlas_tile` keys detected!")

def fonts_fix_font_aliases(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    return {font["alias"]: font for font in data}

def fonts_fix_font_references(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    return {font["font_reference"]: font for font in data}

def fonts_fix_fonts(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    return {font["font_name"]: font for font in data}

def gui_routes_normalize(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    return {route["fileName"]: route for route in data}

def gui_routes_supported_routes_normalize(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    return {route["route"]: route for route in data}

def gui_routes_params_normalize(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    return {route["name"]: route for route in data}

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

def loot_tables_normalize_conditions(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    output = {condition["condition"]: (condition) for condition in data}
    for condition in output.values():
        del condition["condition"]
    return output

def loot_tables_normalize_functions(data:list[dict[str,str]]) -> dict[str,dict[str,str]]:
    output = {function["function"]: function for function in data}
    for function in output.values():
        del function["function"]
    return output

def materials_normalize_material(data:dict[str,dict[str,Any]]) -> dict[str,dict[str,Any]]|None:
    if "materials" in data:
        data["version"] = data["materials"]["version"]
    else:
        return {"materials": data, "defined_in": data["defined_in"]}

def materials_remove_extra_keys(data:dict[str,str]) -> None:
    if "version" in data:
        del data["version"]
    if "defined_in" in data:
        del data["defined_in"]

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

def models_normalize_bones(data:list[DataMinerTyping.ModelBoneTypedDict]) -> dict[str,DataMinerTyping.ModelBoneTypedDict]:
    return {bone["name"]: bone for bone in data}

def models_remove_bone_name(data:dict[str,str]) -> None:
    del data["name"]

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

def particles_remove_weird_components(data:dict[str,Any]) -> None:
    if "minecraft:particle_appearance_tinting" in data:
        del data["minecraft:particle_appearance_tinting"]
    if "minecraft:particle_appearance_lighting" in data:
        del data["minecraft:particle_appearance_lighting"]

def resource_packs_normalize(data:DataMinerTyping.ResourcePacks) -> list[str]:
    return [resource_pack["name"] for resource_pack in data]

def render_controllers_fix_old(data:dict[str,Any]) -> dict[str,Any]|None:
    if "render_controllers" in data: return
    defined_in = data["defined_in"]
    del data["defined_in"]
    return {"defined_in": defined_in, "render_controllers": data}

def render_controllers_remove_texures(data:dict[str,Any]) -> None:
    if "texures" in data:
        del data["texures"]

def renderer_platform_configuration_normalize_shadow_config(data:dict[str,str]) -> dict[str,dict[str,str]]|None:
    if "file" in data:
        return {"shadow_config": data}

def sound_definitions_fix_MCPE_153558(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153558
    if "pitch" in data:
        del data["pitch"]

def sound_definitions_fix_MCPE_178265(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-178265
    if "volume" in data:
        del data["volume"]

def sound_definitions_make_strings_to_dict(data:str|DataMinerTyping.SoundDefinitionsJsonSoundTypedDict) -> DataMinerTyping.SoundDefinitionsJsonSoundTypedDict|None:
    if isinstance(data, str):
        return {"name": data}

def sound_definitions_fix_MCPE_153561(data:DataMinerTyping.SoundDefinitionsJsonSoundTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153561
    if "pitch:" in data:
        del data["pitch:"]

def sound_files_remove_obj(data:DataMinerTyping.SoundFilesTypedDict) -> None:
    if "_obj" in data:
        del data["_obj"]

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

def sounds_json_remove_weird_keys(data:DataMinerTyping.SoundsJsonSoundTypedDict) -> None:
    if "ambient" in data:
        del data["ambient"]
    if "death" in data:
        del data["death"]
    if "hurt" in data:
        del data["hurt"]
    if "attenuation_distance" in data:
        del data["attenuation_distance"]

def sounds_json_fix_sounds(data:DataMinerTyping.SoundsJsonSoundTypedDict) -> None:
    '''moves key "sounds" to "sound". It occurs a whole lot and for a long time, so it's gotta be on purpose.'''
    # TODO: find out if "sounds" is actually a valid key.
    if "sounds" in data:
        data["sound"] = data["sounds"]
        del data["sounds"]

def spawn_rules_normalize_herd(data:dict[str,Any]|list[dict[str,Any]]) -> list[dict[str,Any]]|None:
    if isinstance(data, dict):
        return [data]

def structures_nbt_normalize_text(data:NbtTypes.TAG_String) -> dict[str,str]:
    return json.loads(data.value)

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

def terrain_meta_normalize(data:list[dict[str,Any]]) -> dict[str,dict[str,Any]]:
    return {item["name"]: item for item in data}

terrain_meta_normalize_uvs_keys = ("x1", "y1", "x2", "y2", "1", "2")
def terrain_meta_normalize_uv(data:list[int|float]) -> dict[str,int|float]:
    return {key: value for key, value in zip(terrain_meta_normalize_uvs_keys, data)}

def terrain_meta_remove_name(data:dict[str,str]) -> None:
    del data["name"]

def texture_list_normalize(data:dict[str,list[str]]) -> dict[str,list[str]]:
    output:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack, textures in data.items():
        for texture in textures:
            output[texture].append(resource_pack)
    return dict(output)

functions:dict[str,Callable] = {
    "collapse_resource_pack_names": CollapseResourcePacks.collapse_resource_pack_names,
    "collapse_resource_packs_dict_with_defined_in": CollapseResourcePacks.make_dict_interface(has_defined_in_key=True),
    "collapse_resource_packs_dict_without_defined_in": CollapseResourcePacks.make_dict_interface(has_defined_in_key=False),
    "collapse_resource_packs_list": CollapseResourcePacks.collapse_resource_packs_list,
    "collapse_resource_packs_flat": CollapseResourcePacks.collapse_resource_packs_flat,
    "animation_controllers_fix_old": animation_controllers_fix_old,
    "animations_fix_old": animations_fix_old,
    "attachables_normalize_old": attachables_normalize_old,
    "behavior_packs_normalize": behavior_packs_normalize,
    "biomes_normalize_old": biomes_normalize_old,
    "blocks_client_fix_MCPE_76182": blocks_client_fix_MCPE_76182,
    "blocks_client_normalize": blocks_client_normalize,
    "credits_normalize_sections": credits_normalize_sections,
    "credits_normalize_disciplines": credits_normalize_disciplines,
    "credits_normalize_titles": credits_normalize_titles,
    "entities_fix_event_bug": entities_fix_event_bug,
    "entities_fix_out_of_bounds_components": entities_fix_out_of_bounds_components,
    "entities_fix_MCPE_178417": entities_fix_MCPE_178417,
    "entities_fix_invalid_components": entities_fix_invalid_components,
    "entities_fix_priotiry": entities_fix_priotiry,
    "entities_client_fix_old": entities_client_fix_old,
    "features_fix_growing_plant_feature_body_blocks": features_fix_growing_plant_feature_body_blocks,
    "features_fix_growing_plant_feature_head_blocks": features_fix_growing_plant_feature_head_blocks,
    "features_fix_growing_plant_feature_height_distribution": features_fix_growing_plant_feature_height_distribution,
    "features_fix_tree_feature_canopy_leaf_blocks": features_fix_tree_feature_canopy_leaf_blocks,
    "features_fix_weighted_random_features": features_fix_weighted_random_features,
    "flipbook_textures_fix_flipbook_textures": flipbook_textures_fix_flipbook_textures,
    "fonts_fix_font_aliases": fonts_fix_font_aliases,
    "fonts_fix_font_references": fonts_fix_font_references,
    "fonts_fix_fonts": fonts_fix_fonts,
    "gui_routes_normalize": gui_routes_normalize,
    "gui_routes_supported_routes_normalize": gui_routes_supported_routes_normalize,
    "gui_routes_params_normalize": gui_routes_params_normalize,
    "item_textures_normalize": item_textures_normalize,
    "recipes_fix_old": recipes_fix_old,
    "languages_normalize": languages_normalize,
    "loot_tables_normalize_conditions": loot_tables_normalize_conditions,
    "loot_tables_normalize_functions": loot_tables_normalize_functions,
    "materials_normalize_material": materials_normalize_material,
    "materials_remove_extra_keys": materials_remove_extra_keys,
    "models_model_normalize": models_model_normalize,
    "models_normalize_bones": models_normalize_bones,
    "models_remove_bone_name": models_remove_bone_name,
    "particles_normalize_component_particle_appearance_tinting_color": particles_normalize_component_particle_appearance_tinting_color,
    "particles_normalize_old": particles_normalize_old,
    "particles_remove_weird_components": particles_remove_weird_components,
    "resource_packs_normalize": resource_packs_normalize,
    "render_controllers_fix_old": render_controllers_fix_old,
    "render_controllers_remove_texures": render_controllers_remove_texures,
    "renderer_platform_configuration_normalize_shadow_config": renderer_platform_configuration_normalize_shadow_config,
    "sound_definitions_fix_MCPE_153558": sound_definitions_fix_MCPE_153558,
    "sound_definitions_fix_MCPE_178265": sound_definitions_fix_MCPE_178265,
    "sound_definitions_make_strings_to_dict": sound_definitions_make_strings_to_dict,
    "sound_definitions_fix_MCPE_153561": sound_definitions_fix_MCPE_153561,
    "sound_files_remove_obj": sound_files_remove_obj,
    "sounds_json_remove_bad_events": sounds_json_remove_bad_events,
    "sounds_json_remove_bad_interactive_entity_events": sounds_json_remove_bad_interactive_entity_events,
    "sounds_json_remove_weird_keys": sounds_json_remove_weird_keys,
    "sounds_json_fix_sounds": sounds_json_fix_sounds,
    "spawn_rules_normalize_herd": spawn_rules_normalize_herd,
    "structures_nbt_normalize_text": structures_nbt_normalize_text,
    "terrain_textures_normalize": terrain_textures_normalize,
    "terrain_meta_normalize": terrain_meta_normalize,
    "terrain_meta_normalize_uv": terrain_meta_normalize_uv,
    "terrain_meta_remove_name": terrain_meta_remove_name,
    "texture_list_normalize": texture_list_normalize,
}
