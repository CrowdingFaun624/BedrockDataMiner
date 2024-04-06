from typing import Any, Callable, cast

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

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

def behavior_packs_normalize(data:DataMinerTyping.BehaviorPacks, dependencies:DataMinerTyping.DependenciesTypedDict) -> list[str]:
    return [behavior_pack["name"] for behavior_pack in data]

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

    def fix_properties(unfixed_data:DataMinerTyping.LanguagesTypedDict, resource_packs:DataMinerTyping.ResourcePacks) -> dict[str,Any]:
        output:dict[str,DataMinerTyping.LanguagesPropertiesTypedDict] = unfixed_data["properties"]
        for resource_pack in unfixed_data["defined_in"]:
            if resource_pack not in output:
                output[resource_pack] = {}
        return CollapseResourcePacks.collapse_resource_packs(output, resource_packs)

    resource_packs:DataMinerTyping.ResourcePacks|None = dependencies["resource_packs"]
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]

    return {language["code"]: fix_properties(language, resource_packs) for language in data}

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

structures_resource_pack_move = lambda key, value: value["hash"]

structures_structure_move = lambda key, value: [resource_pack["hash"] for resource_pack in value.values()]

texture_list_comparison_move_function = lambda key, value: key

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
    "collapse_behavior_pack_list": CollapseResourcePacks.make_interface_list(pack_key="behavior_packs"),
    "collapse_resource_pack_list": CollapseResourcePacks.make_interface_list(pack_key="resource_packs"),
    "collapse_behavior_packs_or_resource_packs_with_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=True, pack_key=["behavior_packs", "resource_packs"]),
    "collapse_behavior_packs_with_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=True, pack_key="behavior_packs"),
    "collapse_behavior_packs_without_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=False, pack_key="behavior_packs"),
    "collapse_resource_packs_with_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=True, pack_key="resource_packs"),
    "collapse_resource_packs_without_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=False, pack_key="resource_packs"),
    "animation_controllers_fix_old": animation_controllers_fix_old,
    "animations_fix_old": animations_fix_old,
    "behavior_packs_normalize": behavior_packs_normalize,
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
    "item_textures_normalize": item_textures_normalize,
    "items_behavior_pack_comparison_move_function": items_behavior_pack_comparison_move_function,
    "items_fix_old": items_fix_old,
    "language_comparison_move_function": language_comparison_move_function,
    "languages_normalize": languages_normalize,
    "loot_tables_behavior_pack_comparison_move_function": loot_tables_behavior_pack_comparison_move_function,
    "loot_tables_normalize_conditions": loot_tables_normalize_conditions,
    "loot_tables_normalize_functions": loot_tables_normalize_functions,
    "models_model_normalize": models_model_normalize,
    "models_normalize_bones": models_normalize_bones,
    "recipes_behavior_pack_comparison_move_function": recipes_behavior_pack_comparison_move_function,
    "resource_packs_normalize": resource_packs_normalize,
    "render_controllers_fix_old": render_controllers_fix_old,
    "render_controllers_remove_texures": render_controllers_remove_texures,
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
    "structures_resource_pack_move": structures_resource_pack_move,
    "structures_structure_move": structures_structure_move,
    "texture_list_comparison_move_function": texture_list_comparison_move_function,
    "texture_list_normalize": texture_list_normalize,
}
