import json
from typing import Any, Callable, cast, TypedDict

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Utilities.Nbt.NbtTypes as NbtTypes

def animation_controllers_fix_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "animation_controllers" in data: return
    if "defined_in" in data:
        del data["defined_in"]
    output = data.copy()
    for key in list(data.keys()):
        if not key.startswith("controller.animation"):
            raise RuntimeError("Weird animation controller key \"%s\" does not start with \"controller.animation\"!" % key)
        del data[key]
    data["animation_controllers"] = output

def animations_fix_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "animations" in data: return
    if "defined_in" in data:
        del data["defined_in"]
    output = data.copy()
    for key in list(data.keys()):
        if not key.startswith("animation"):
            raise RuntimeError("Weird animation key \"%s\" does not start with \"animation\"!" % key)
        del data[key]
    data["animations"] = output

def attachables_normalize_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "minecraft:attachable" in data:
        return
    attachable_identifier = list(data.keys())[0]
    result = {"description": data[attachable_identifier]}
    del data[attachable_identifier]
    result["description"]["identifier"] = attachable_identifier

def behavior_packs_normalize(data:DataMinerTyping.BehaviorPacks, dependencies:DataMinerTyping.DependenciesTypedDict) -> list[str]:
    return [behavior_pack["name"] for behavior_pack in data]

def biomes_normalize_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "minecraft:biome" in data: return
    if len(data) != 1:
        raise RuntimeError("Expected 1 key, but got [%s]" % (list(data.keys()),))
    biome_name = list(data.keys())[0]
    format_version = data[biome_name].get("format_version")
    result = {}
    if format_version is not None:
        del data[biome_name]["format_version"]
        result["format_version"] = format_version
    result["minecraft:biome"] = {"components": data[biome_name], "description": {"identifier": biome_name}}
    del data[biome_name]
    data.update(result)

def blocks_client_fix_MCPE_76182(data:DataMinerTyping.BlocksJsonClientBlockTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-76182
    if "sounds" in data:
        del data["sounds"]

def blocks_client_normalize(data:DataMinerTyping.MyBlocksClient, dependencies:DataMinerTyping.DependenciesTypedDict) -> dict[str,DataMinerTyping.BlocksJsonClientBlockTypedDict]:
    return {block["name"]: block["properties"] for block in data}

def blocks_client_resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

def credits_normalize_sections(data:DataMinerTyping.Credits, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedCredits:
    return {section["section"]: section for section in data}

def credits_normalize_disciplines(data:Any, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "disciplines" not in data: return
    data["disciplines"] = {discipline["discipline"]: discipline for discipline in data["disciplines"]}

def credits_normalize_titles(data:Any, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "titles" not in data: return
    data["titles"] = {title["title"]: title for title in data["titles"]}

def entities_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    if "defined_in" in output:
        del output["defined_in"]
    return output

def entities_fix_event_bug(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "minecraft:transformation" in data:
        del data["minecraft:transformation"]

def entities_fix_out_of_bounds_components(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for key_to_delete in [key for key in data if key.startswith("minecraft:")]:
        del data[key_to_delete]

def entities_fix_MCPE_178417(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-178417
    for key_to_delete in [key for key in data if key.startswith("minecraft:")]:
        del data[key_to_delete]

def entities_fix_invalid_components(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "minecart:on_hurt_by_player" in data:
        del data["minecart:on_hurt_by_player"]

def entities_fix_priotiry(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "priotiry" in data:
        del data["priotiry"]

def entities_client_fix_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "minecraft:client_entity" in data: return
    if "defined_in" in data:
        del data["defined_in"]
    if len(data) != 1:
        raise ValueError("Data has too many entity clients: [%s]!" % (", ".join(data.keys())))
    entity_client_name = list(data.keys())[0]
    output = data[entity_client_name]
    del data[entity_client_name]
    data["minecraft:client_entity"] = {"description": output}

def features_fix_growing_plant_feature_body_blocks(data:list[list[Any]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for index, item in enumerate(data):
        assert len(item) == 2
        data[index] = {"plant_body_block": item[0], "weight": item[1]}

def features_fix_growing_plant_feature_head_blocks(data:list[list[Any]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for index, item in enumerate(data):
        assert len(item) == 2
        data[index] = {"plant_head_block": item[0], "weight": item[1]}

def features_fix_growing_plant_feature_height_distribution(data:list[list[Any]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for index, item in enumerate(data):
        assert len(item) == 2
        data[index] = {"height": item[0], "weight": item[1]}

def features_fix_tree_feature_canopy_leaf_blocks(data:dict[str,list[Any]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "leaf_blocks" in data:
        for index, item in enumerate(data):
            assert len(item) == 2
            data[index] = {"leaf_block": item[0], "weight": item[1]}

def features_fix_weighted_random_features(data:list[list[Any]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for index, item in enumerate(data):
        assert len(item) == 2
        data[index] = {"feature": item[0], "weight": item[1]}

def flipbook_textures_fix_flipbook_textures(data:dict[str,list[dict[str,str]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for resource_pack_name, resource_pack_data in data.items():
        start_length = len(resource_pack_data)
        data[resource_pack_name] = {flipbook_texture["atlas_tile"]: flipbook_texture for flipbook_texture in resource_pack_data}
        if len(resource_pack_data) != start_length:
            raise RuntimeError("Duplicate `atlas_tile` keys detected!")

flipbook_textures_texture_move_function:Callable[[str, dict[str,str]],str] = lambda key, value: value["flipbook_texture"]

def fonts_fix_font_aliases(data:dict[str,list[dict[str,str]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "font_aliases" not in data: return
    output:dict[str,dict[str,str]] = {}
    for font in data["font_aliases"]:
        output[font["alias"]] = font
    data["font_aliases"] = output

def fonts_fix_font_references(data:dict[str,list[dict[str,str]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "fonts" not in data: return
    output:dict[str,dict[str,str]] = {}
    for font in data["fonts"]:
        output[font["font_reference"]] = font
    data["fonts"] = output

def fonts_fix_fonts(data:dict[str,list[dict[str,str]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "fonts" not in data: return
    output:dict[str,dict[str,str]] = {}
    for font in data["fonts"]:
        output[font["font_name"]] = font
    data["fonts"] = output

def fonts_font_comparison_move_function(key:str, value:dict[str,str]) -> str|None:
    return value.get("font_file", None)

def gui_routes_normalize(data:dict[str,list[dict[str,str]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    assert "routes" in data
    data["routes"] = {route["fileName"]: route for route in data["routes"]}

def gui_routes_supported_routes_normalize(data:dict[str,list[dict[str,str]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    assert "supportedRoutes" in data
    data["supportedRoutes"] = {route["route"]: route for route in data["supportedRoutes"]}

def gui_routes_params_normalize(data:dict[str,list[dict[str,str]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    assert "params" in data
    data["params"] = {route["name"]: route for route in data["params"]}

identity_move_function = lambda key, value: value

def item_textures_normalize(data:dict[str,dict[str,dict[str,dict[str,str]]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> dict[str,Any]:
    output:dict[str,dict[str,Any]] = {}
    for resource_pack_name, item_textures_data in data.items():
        for item, item_data in item_textures_data["texture_data"].items():
            if item in output:
                output[item][resource_pack_name] = item_data
            else:
                output[item] = {resource_pack_name: item_data}
    return output

def items_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def items_fix_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "type" not in data: return
    old_recipe_type = data["type"]
    del data["type"]
    del data["defined_in"]
    new_recipe_types = {
        "crafting_shaped": "minecraft:recipe_shaped",
        "crafting_shapeless": "minecraft:recipe_shapeless",
        "furnace_recipe": "minecraft:recipe_furnace",
    }
    if old_recipe_type not in new_recipe_types:
        raise KeyError("Recipe type \"%s\" not recognized!" % old_recipe_type)
    new_recipe_type = new_recipe_types[old_recipe_type]
    output = data.copy()
    for key in list(data.keys()):
        del data[key]
    data[new_recipe_type] = output

language_comparison_move_function:Callable[[str, DataMinerTyping.LanguageTypedDict], str] = lambda key, value: value["value"]

def languages_normalize(data:DataMinerTyping.Languages, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedLanguages:

    def fix_properties(unfixed_data:DataMinerTyping.LanguagesTypedDict) -> dict[str,Any]:
        output:dict[str,DataMinerTyping.LanguagesPropertiesTypedDict] = unfixed_data["properties"]
        for resource_pack in unfixed_data["defined_in"]:
            if resource_pack not in output:
                output[resource_pack] = {}
        return CollapseResourcePacks.collapse_resource_packs(output)
    return {language["code"]: fix_properties(language) for language in data}

def loot_tables_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def loot_tables_normalize_conditions(data:DataMinerTyping.LootTableHasConditions, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "conditions" not in data: return
    output:dict[str,DataMinerTyping.LootTableConditions] = {}
    for condition in data["conditions"]:
        assert isinstance(condition, dict)
        assert "condition" in condition
        condition_name = condition["condition"]
        output[condition_name] = condition
        del condition["condition"]
    data["conditions"] = output

def loot_tables_normalize_functions(data:DataMinerTyping.LootTableHasFunctions, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "functions" not in data: return
    output:dict[str,DataMinerTyping.LootTableFunctions] = {}
    for function in data["functions"]:
        assert isinstance(function, dict)
        assert "function" in function
        function_name = function["function"]
        output[function_name] = function
        del function["function"]
    data["functions"] = output

def materials_normalize_material(data:dict[str,dict[str,Any]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "materials" in data:
        assert set(data.keys()) == {"defined_in", "materials"}
        version:str = data["materials"]["version"]
        data["version"] = version
        del data["materials"]["version"]
    else:
        materials = data.copy()
        data.clear()
        data["materials"] = materials
        if "defined_in" in data["materials"]:
            defined_in = data["materials"]["defined_in"]
            del data["materials"]["defined_in"]
            data["defined_in"] = defined_in

def models_model_normalize(data:dict[str,dict[str,dict[str,Any]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> dict[str,Any]:
    output:dict[str,Any] = {}
    for model_file_name, resource_packs in data.items():
        for resource_pack_name, model_file_data in resource_packs.items():
            if "minecraft:geometry" in model_file_data:
                format_version:str|None = model_file_data["format_version"]
                assert isinstance(model_file_data["minecraft:geometry"], list)
                for geometry_item in model_file_data["minecraft:geometry"]:
                    name = geometry_item["description"]["identifier"]
                    model_output_name = "%s %s" % (model_file_name, name)
                    output_data = {"format_version": format_version, "minecraft:geometry": geometry_item}
                    if model_output_name in output:
                        if resource_pack_name in output[model_output_name]:
                            raise KeyError("Multiple models using name \"%s\" and resource pack \"%s\"!" % (model_output_name, resource_pack_name))
                        output[model_output_name][resource_pack_name] = output_data
                    else:
                        output[model_output_name] = {resource_pack_name: output_data}
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
                    output_data = {"format_version": format_version, "minecraft:geometry": model_data}
                    if model_output_name in output:
                        if resource_pack_name in output[model_output_name]:
                            raise KeyError("Multiple models using name \"%s\" and resource pack \"%s\"!" % (model_output_name, resource_pack_name))
                        output[model_output_name][resource_pack_name] = output_data
                    else:
                        output[model_output_name] = {resource_pack_name: output_data}
    return output

def models_normalize_bones(data:DataMinerTyping.ModelGeometryTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "bones" in data:
        output:dict[str,Any] = {}
        for bone in data["bones"]:
            assert "name" in bone
            assert isinstance(bone, dict)
            name = bone["name"]
            del bone["name"]
            output[name] = bone
        data["bones"] = output

is_valid_color:Callable[[Any],bool] = lambda color: (isinstance(color, list) and len(color) in (3, 4) and all(isinstance(channel, (int, float, str)) for channel in color)) or isinstance(color, str)
def particles_normalize_component_particle_appearance_tinting_color(data:dict[str,str|list[int]|dict[str,str|list[int]]|list[str|list[int]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "color" not in data: return
    if is_valid_color(data["color"]):
        data["color"] = [data["color"]]

def particles_normalize_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "particles" not in data:
        return
    assert len(data["particles"]) == 1
    particle_identifier:str = list(data["particles"].keys())[0]
    data["particle_effect"] = data["particles"][particle_identifier]
    del data["particles"]
    data["particle_effect"]["description"] = {"basic_render_parameters": data["particle_effect"]["basic_render_parameters"], "identifier": particle_identifier}
    del data["particle_effect"]["basic_render_parameters"]

def particles_remove_weird_components(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "minecraft:particle_appearance_tinting" in data:
        del data["minecraft:particle_appearance_tinting"]
    if "minecraft:particle_appearance_lighting" in data:
        del data["minecraft:particle_appearance_lighting"]

def recipes_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def resource_packs_normalize(data:DataMinerTyping.ResourcePacks, dependencies:DataMinerTyping.DependenciesTypedDict) -> list[str]:
    return [resource_pack["name"] for resource_pack in data]

def render_controllers_fix_old(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "render_controllers" in data: return
    if "defined_in" in data:
        del data["defined_in"]
    output = data.copy()
    for key in list(data.keys()):
        del data[key]
    data["render_controllers"] = output

def render_controllers_remove_texures(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "texures" in data:
        del data["texures"]

def renderer_platform_configuration_normalize_shadow_config(data:dict[str,str], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "file" in data:
        data["shadow_config"] = {"file": data["file"]}
        del data["file"]

def sound_definitions_fix_MCPE_153558(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153558
    if "pitch" in data:
        del data["pitch"]

def sound_definitions_fix_MCPE_178265(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-178265
    if "volume" in data:
        del data["volume"]

def sound_definitions_make_sounds_dict(data:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "sounds" in data:
        sounds:dict[str,DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict] = {}
        for sound in data["sounds"]:
            if isinstance(sound, str):
                sounds[sound] = {}
            else:
                name = sound["name"]
                sound = cast(DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict, sound)
                del sound["name"]
                sounds[name] = sound
        data["sounds"] = sounds

def sound_definitions_fix_MCPE_153561(data:DataMinerTyping.SoundDefinitionsJsonSoundTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153561
    if "pitch:" in data:
        del data["pitch:"]

def sound_definitions_resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundEventTypedDict) -> DataMinerTyping.NormalizedSoundDefinitionsJsonSoundEventTypedDict:
    output = value.copy()
    del value["defined_in"]
    return output

def sound_definitions_sound_comparison_move_function(key:str, value:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict) -> str:
    return key.split("/")[-1]

def sound_files_remove_obj(data:DataMinerTyping.SoundFilesTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "_obj" in data:
        del data["_obj"]

def sound_files_sound_file_comparison_move_function(key:str, value:dict[str,DataMinerTyping.NormalizedSoundFilesTypedDict]) -> dict[str,str]:
    return {internal_sound_file_name: internal_sound_file_properties["sha1_hash"] for internal_sound_file_name, internal_sound_file_properties in value.items()}

sound_files_internal_sound_file_comparison_move_function = lambda key, value: value["sha1_hash"]

def sounds_json_remove_bad_events(data:dict[str,str|DataMinerTyping.SoundsJsonSoundTypedDict], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    events_to_delete:list[str] = []
    for event_name, event_properties in data.items():
        if isinstance(event_properties, str): continue
        if "sound" not in event_properties and "sounds" not in event_properties:
            events_to_delete.append(event_name)
    for event_to_delete in events_to_delete:
        del data[event_to_delete]

def sounds_json_remove_bad_interactive_entity_events(data:dict[str,dict[str,str]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    events_to_delete:list[str] = []
    for event_name, event_properties in data.items():
        if isinstance(event_properties, str): continue
        if "default" not in event_properties:
            events_to_delete.append(event_name)
    for event_to_delete in events_to_delete:
        del data[event_to_delete]

def sounds_json_fix_sounds(data:DataMinerTyping.SoundsJsonSoundTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    '''moves key "sounds" to "sound". It occurs a whole lot and for a long time, so it's gotta be on purpose.'''
    # TODO: find out if "sounds" is actually a valid key.
    for key in [key for key in data.keys() if key not in ("sound", "sounds", "volume", "pitch")]:
        del data[key]
    if "sounds" in data:
        assert "sound" not in data or data["sound"] == data["sounds"]
        data["sound"] = data["sounds"]
        del data["sounds"]

sounds_json_sound_collections_comparison_move_function = lambda key, value: None if len(value) == 0 else value

def spawn_rules_normalize_herd(data:dict[str,dict[str,Any]|list[dict[str,Any]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "minecraft:herd" not in data: return
    if isinstance(data["minecraft:herd"], dict):
        data["minecraft:herd"] = {"": data["minecraft:herd"]} # placing it into a nested dict is easier since the base case with the max_size and min_size has the same type as what I'm normalizing it to.
    else:
        data["minecraft:herd"] = {item["event"]: item for item in data["minecraft:herd"]}
        for item in data["minecraft:herd"].values():
            del item["event"]

structures_resource_pack_move:Callable[[str, NbtTypes.TAG_Compound],int|None] = lambda key, value: value.hash

structures_structure_move:Callable[[str, dict[str,NbtTypes.TAG_Compound]],list[int|None]] = lambda key, value: [resource_pack.hash for resource_pack in value.values()]

structures_nbt_normalize_text_keys = ["Text%i" % i for i in range(1, 5)]
def structures_nbt_normalize_text(data:dict[str,NbtTypes.TAG_String], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for key in structures_nbt_normalize_text_keys:
        if key in data:
            data[key] = json.loads(data[key].value)

texture_list_comparison_move_function = lambda key, value: key

terrain_textures_normalize_typed_dict = TypedDict("terrain_textures_normalize_typed_dict", {"resource_pack_name": str, "texture_name": str, "padding": int, "num_mip_levels": int, "texture_data": dict[str,dict[str,str]]})
def terrain_textures_normalize(data:dict[str,terrain_textures_normalize_typed_dict], dependencies:DataMinerTyping.DependenciesTypedDict) -> dict[str,Any]:
    normal_keys = set(["resource_pack_name", "texture_name", "padding", "num_mip_levels", "texture_data"])
    other_keys = {"texture_name": {}, "padding": {}, "num_mip_levels": {}}
    texture_data:dict[str,dict[str,Any]] = {}
    for resource_pack_name, terrain_textures_data in data.items():
        assert set(terrain_textures_data.keys()) == normal_keys
        for other_key_key, other_key_values in other_keys.items():
            if other_key_key in terrain_textures_data:
                other_key_values[resource_pack_name] = terrain_textures_data[other_key_key]
        for terrain, terrain_data in terrain_textures_data["texture_data"].items():
            if terrain in texture_data:
                texture_data[terrain][resource_pack_name] = terrain_data
            else:
                texture_data[terrain] = {resource_pack_name: terrain_data}
    output = other_keys
    output["texture_data"] = texture_data
    return output

def terrain_meta_normalize(data:list[dict[str,Any]], dependencies:DataMinerTyping.DependenciesTypedDict) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = {}
    for item in data:
        output[item["name"]] = item
        del item["name"]
    return output

terrain_meta_normalize_uvs_keys = ("x1", "y1", "x2", "y2", "1", "2")
def terrain_meta_normalize_uv(data:dict[str,list[int]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "uv" not in data: return
    data["uv"] = {key: value for key, value in zip(terrain_meta_normalize_uvs_keys, data["uv"])}

def terrain_meta_normalize_uvs(data:list[list[int]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for index, uv in enumerate(data):
        assert len(uv) == 6
        data[index] = {key: value for key, value in zip(terrain_meta_normalize_uvs_keys, uv)}

def texture_list_normalize(data:dict[str,list[str]], dependencies:DataMinerTyping.DependenciesTypedDict) -> dict[str,list[str]]:
    output:dict[str,list[str]] = {}
    for resource_pack, textures in data.items():
        for texture in textures:
            if texture in output:
                output[texture].append(resource_pack)
            else:
                output[texture] = [resource_pack]
    return output

functions:dict[str,Callable] = {
    "collapse_behavior_pack_list": CollapseResourcePacks.collapse_resource_pack_list,
    "collapse_resource_pack_list": CollapseResourcePacks.collapse_resource_pack_list,
    "collapse_resource_packs_with_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=True),
    "collapse_resource_packs_without_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=False),
    "animation_controllers_fix_old": animation_controllers_fix_old,
    "animations_fix_old": animations_fix_old,
    "attachables_normalize_old": attachables_normalize_old,
    "behavior_packs_normalize": behavior_packs_normalize,
    "biomes_normalize_old": biomes_normalize_old,
    "blocks_client_fix_MCPE_76182": blocks_client_fix_MCPE_76182,
    "blocks_client_normalize": blocks_client_normalize,
    "blocks_client_resource_pack_comparison_move_function": blocks_client_resource_pack_comparison_move_function,
    "credits_normalize_sections": credits_normalize_sections,
    "credits_normalize_disciplines": credits_normalize_disciplines,
    "credits_normalize_titles": credits_normalize_titles,
    "entities_behavior_pack_comparison_move_function": entities_behavior_pack_comparison_move_function,
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
    "flipbook_textures_texture_move_function": flipbook_textures_texture_move_function,
    "fonts_fix_font_aliases": fonts_fix_font_aliases,
    "fonts_fix_font_references": fonts_fix_font_references,
    "fonts_fix_fonts": fonts_fix_fonts,
    "fonts_font_comparison_move_function": fonts_font_comparison_move_function,
    "gui_routes_normalize": gui_routes_normalize,
    "gui_routes_supported_routes_normalize": gui_routes_supported_routes_normalize,
    "gui_routes_params_normalize": gui_routes_params_normalize,
    "identity_move_function": identity_move_function,
    "item_textures_normalize": item_textures_normalize,
    "items_behavior_pack_comparison_move_function": items_behavior_pack_comparison_move_function,
    "items_fix_old": items_fix_old,
    "language_comparison_move_function": language_comparison_move_function,
    "languages_normalize": languages_normalize,
    "loot_tables_behavior_pack_comparison_move_function": loot_tables_behavior_pack_comparison_move_function,
    "loot_tables_normalize_conditions": loot_tables_normalize_conditions,
    "loot_tables_normalize_functions": loot_tables_normalize_functions,
    "materials_normalize_material": materials_normalize_material,
    "models_model_normalize": models_model_normalize,
    "models_normalize_bones": models_normalize_bones,
    "particles_normalize_component_particle_appearance_tinting_color": particles_normalize_component_particle_appearance_tinting_color,
    "particles_normalize_old": particles_normalize_old,
    "particles_remove_weird_components": particles_remove_weird_components,
    "recipes_behavior_pack_comparison_move_function": recipes_behavior_pack_comparison_move_function,
    "resource_packs_normalize": resource_packs_normalize,
    "render_controllers_fix_old": render_controllers_fix_old,
    "render_controllers_remove_texures": render_controllers_remove_texures,
    "renderer_platform_configuration_normalize_shadow_config": renderer_platform_configuration_normalize_shadow_config,
    "sound_definitions_fix_MCPE_153558": sound_definitions_fix_MCPE_153558,
    "sound_definitions_fix_MCPE_178265": sound_definitions_fix_MCPE_178265,
    "sound_definitions_make_sounds_dict": sound_definitions_make_sounds_dict,
    "sound_definitions_fix_MCPE_153561": sound_definitions_fix_MCPE_153561,
    "sound_definitions_resource_pack_comparison_move_function": sound_definitions_resource_pack_comparison_move_function,
    "sound_definitions_sound_comparison_move_function": sound_definitions_sound_comparison_move_function,
    "sound_files_remove_obj": sound_files_remove_obj,
    "sound_files_sound_file_comparison_move_function": sound_files_sound_file_comparison_move_function,
    "sound_files_internal_sound_file_comparison_move_function": sound_files_internal_sound_file_comparison_move_function,
    "sounds_json_remove_bad_events": sounds_json_remove_bad_events,
    "sounds_json_remove_bad_interactive_entity_events": sounds_json_remove_bad_interactive_entity_events,
    "sounds_json_fix_sounds": sounds_json_fix_sounds,
    "sounds_json_sound_collections_comparison_move_function": sounds_json_sound_collections_comparison_move_function,
    "spawn_rules_normalize_herd": spawn_rules_normalize_herd,
    "structures_resource_pack_move": structures_resource_pack_move,
    "structures_structure_move": structures_structure_move,
    "structures_nbt_normalize_text": structures_nbt_normalize_text,
    "terrain_textures_normalize": terrain_textures_normalize,
    "terrain_meta_normalize": terrain_meta_normalize,
    "terrain_meta_normalize_uv": terrain_meta_normalize_uv,
    "terrain_meta_normalize_uvs": terrain_meta_normalize_uvs,
    "texture_list_comparison_move_function": texture_list_comparison_move_function,
    "texture_list_normalize": texture_list_normalize,
}
