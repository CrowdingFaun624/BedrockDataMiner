from typing import Any, Callable

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

def behavior_packs_normalize(data:DataMinerTyping.BehaviorPacks, dependencies:DataMinerTyping.DependenciesTypedDict) -> list[str]:
    return [behavior_pack["name"] for behavior_pack in data]

def blocks_client_fix_MCPE_76182(data:DataMinerTyping.BlocksJsonClientBlockTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-76182
    if "sounds" in data:
        del data["sounds"]

def blocks_client_normalize(data:DataMinerTyping.MyBlocksClient, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedBlocksClient:
    return {block["name"]: block["properties"] for block in data}

def blocks_client_resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonClientBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

def credits_convert(data:DataMinerTyping.Credits, dependencies:DataMinerTyping.DependenciesTypedDict) -> dict:
    return {section["section"]: {discipline["discipline"]: {title["title"]: title["names"] for title in discipline["titles"]} for discipline in section["disciplines"]} for section in data}

def entities_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def entities_fix_out_of_bounds_components(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    for key_to_delete in [key for key in data if key.startswith("minecraft:")]:
        del data[key_to_delete]

def entities_fix_MCPE_178417(data:dict[str,Any], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-178417
    for key_to_delete in [key for key in data if key.startswith("minecraft:")]:
        del data[key_to_delete]

def items_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def languages_normalize(data:DataMinerTyping.Languages, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedLanguages:

    def fix_properties(unfixed_data:DataMinerTyping.LanguagesTypedDict, resource_packs:DataMinerTyping.ResourcePacks) -> dict[str,DataMinerTyping.LanguagesPropertiesTypedDict]:
        output = unfixed_data["properties"]
        for resource_pack in unfixed_data["defined_in"]:
            if resource_pack not in output:
                output[resource_pack] = {}
        return CollapseResourcePacks.collapse_resource_packs(output, resource_packs)

    resource_packs = dependencies["resource_packs"]
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]

    return {language["code"]: fix_properties(language, resource_packs) for language in data}

def languages_languages_comparison_move_function(key:str, value:DataMinerTyping.LanguagesTypedDict) -> dict[str,str]|None:
    output = {resource_pack_name: resource_pack_properties["name"] for resource_pack_name, resource_pack_properties in value.items() if "name" in resource_pack_properties}
    return None if len(output) == 0 else output

def loot_tables_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def loot_tables_normalize_conditions(data:dict[str,list[dict[str,Any]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "conditions" not in data: return
    output:dict[str[dict[str,Any]]] = {}
    for condition in data["conditions"]:
        condition_name = condition["condition"]
        output[condition_name] = condition
        del condition["condition"]
    data["conditions"] = output

def loot_tables_normalize_functions(data:dict[str,list[dict[str,Any]]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "functions" not in data: return
    output:dict[str,dict[str,Any]] = {}
    for function in data["functions"]:
        function_name = function["function"]
        output[function_name] = function
        del function["function"]
    data["functions"] = output

def recipes_behavior_pack_comparison_move_function(key:str, value:dict[str,Any]) -> dict[str,Any]:
    output = value.copy()
    del output["defined_in"]
    return output

def resource_packs_normalize(data:DataMinerTyping.ResourcePacks, dependencies:DataMinerTyping.DependenciesTypedDict) -> list[str]:
    return [resource_pack["name"] for resource_pack in data]

def sound_definitions_fix_MCPE_153558(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153558
    if "pitch" in data:
        del data["pitch"]

def sound_definitions_fix_MCPE_178265(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-178265
    if "volume" in data:
        del data["volume"]

def sound_definitions_make_sounds_dict(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "sounds" in data:
        sounds:dict[str,DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict] = {}
        for sound in data["sounds"]:
            if isinstance(sound, str):
                sounds[sound] = {}
            else:
                sounds[sound["name"]] = sound
                del sound["name"]
        data["sounds"] = sounds

def sound_definitions_fix_MCPE_153561(data:DataMinerTyping.SoundDefinitionsJsonSoundTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153561
    if "pitch:" in data:
        del data["pitch:"]

def sound_definitions_resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundEventTypedDict) -> DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict:
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

functions:dict[str,Callable] = {
    "collapse_behavior_packs_with_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=True, pack_key="behavior_packs"),
    "collapse_behavior_packs_without_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=False, pack_key="behavior_packs"),
    "collapse_resource_packs_with_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=True, pack_key="resource_packs"),
    "collapse_resource_packs_without_defined_in": CollapseResourcePacks.make_interface(has_defined_in_key=False, pack_key="resource_packs"),
    "behavior_packs_normalize": behavior_packs_normalize,
    "blocks_client_fix_MCPE_76182": blocks_client_fix_MCPE_76182,
    "blocks_client_normalize": blocks_client_normalize,
    "blocks_client_resource_pack_comparison_move_function": blocks_client_resource_pack_comparison_move_function,
    "credits_convert": credits_convert,
    "entities_behavior_pack_comparison_move_function": entities_behavior_pack_comparison_move_function,
    "entities_fix_out_of_bounds_components": entities_fix_out_of_bounds_components,
    "entities_fix_MCPE_178417": entities_fix_MCPE_178417,
    "items_behavior_pack_comparison_move_function": items_behavior_pack_comparison_move_function,
    "languages_normalize": languages_normalize,
    "languages_languages_comparison_move_function": languages_languages_comparison_move_function,
    "loot_tables_behavior_pack_comparison_move_function": loot_tables_behavior_pack_comparison_move_function,
    "loot_tables_normalize_conditions": loot_tables_normalize_conditions,
    "loot_tables_normalize_functions": loot_tables_normalize_functions,
    "recipes_behavior_pack_comparison_move_function": recipes_behavior_pack_comparison_move_function,
    "resource_packs_normalize": resource_packs_normalize,
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
}
