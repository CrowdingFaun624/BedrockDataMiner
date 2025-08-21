from typing import Any, Literal, Mapping, Required, TypedDict

from _domains.minecraft_java.scripts.dataminers.PacksDataminer import (
    OutputTypedDict as PacksInputTypedDict,
)
from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Structure.SimpleContainer import SCon
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

domain = get_domain_from_module(__name__)

@component_function(no_arguments=True)
def advancements_display_icon_switch(data:dict[str,Any]|str) -> str:
    if isinstance(data, str):
        return "older"
    elif "item" in data:
        return "old"
    else:
        return "new"

@component_function(no_arguments=True)
def all_files_normalize(data:dict[str,str]) -> dict[str,str]: # remove all .class files
    return {key: value for key, value in data.items() if not key.endswith(".class")}

@component_function(no_arguments=True)
def all_files_data_generator_normalize(data:dict[str,str]) -> dict[str,str]: # remove all cache files
    return {key: value for key, value in data.items() if not key.startswith(".cache")}

@component_function(no_arguments=True)
def block_entity_guess_id(data:dict[str,Any]) -> str|None:
    # 24w34a trial_chambers/spawner/small_melee/slime.nbt and other files
    if (output := data.get("id")) is not None:
        return output
    if "normal_config" in data:
        return "minecraft:trial_spawner"

@component_function(no_arguments=True)
def block_entity_spawn_data_switch(data:dict[str,Any]) -> str:
    return "old" if "id" in data else "new"

@component_function(no_arguments=True)
def carvers_choose(data:dict[str,str]) -> str: # three different versions
    if (output := data.get("type")) is not None:
        return output
    elif (output := data.get("name")) is not None:
        return output
    else:
        return "old"

@component_function(no_arguments=True)
def chat_types_switch(data:dict[str,Any]) -> Literal["old", "new"]:
    return "new" if "translation_key" in data or "parameters" in data or "style" in data else "old"

@component_function(no_arguments=True)
def density_function_switch(data:float|dict) -> str:
    if isinstance(data, (float, int)):
        return "constant_shorthand"
    else:
        assert not isinstance(data, int)
        return data["type"]

@component_function(no_arguments=True)
def data_component_enchantments_switch(data:dict) -> Literal["old", "new"]:
    return "old" if "levels" in data else "new"

@component_function(no_arguments=True)
def feature_simple_block_to_place_switch(data:dict[str,Any]) -> Literal["block_state", "block_state_provider"]:
    if "Name" in data:
        return "block_state"
    else:
        return "block_state_provider"

@component_function(no_arguments=True)
def font_providers_normalize_skip(data:str|list[str]) -> list[str]:
    if isinstance(data, str):
        return list(data)
    else:
        return data

class ItemComponentsOldTypedDict(TypedDict):
    type: Required[str]
    value: Required[Any]

@component_function(no_arguments=True)
def item_components_normalize(data:list[ItemComponentsOldTypedDict]|Mapping[str,Any]) -> Mapping[str,Any]:
    if isinstance(data, list):
        assert all(len(item) == 2 for item in data)
        return {item["type"]: item["value"] for item in data}
    else:
        return data

@component_function(no_arguments=True)
def noise_settings_structure_switch(data:dict[str,Any]) -> Literal["old", "new"]:
    return "new" if "structures" in data or "stronghold" in data else "old"

@component_function(no_arguments=True)
def noise_settings_placement_switch(data:dict[str,Any]) -> str:
    if (output := data.get("type")) is not None:
        return output
    return "new"

@component_function(no_arguments=True)
def old_type_choose(data:dict[str,Any]) -> str:
    if (output := data.get("type")) is not None:
        return output
    return data["name"]

class PacksOutputTypedDict(TypedDict):
    packs: list[str]
    namespaces:list[str]

@component_function(no_arguments=True)
def packs_normalizer(data:PacksInputTypedDict) -> PacksOutputTypedDict:
    return {"packs": list(data["packs"].keys()), "namespaces": list(data["namespaces"].keys())}

@component_function(no_arguments=True)
def post_effect_choose_uniform(data:dict[str,Any]) -> str:
    if (output := data.get("type")) is not None:
        return output
    values_len = len(data["values"])
    if values_len == 1:
        return "float"
    else:
        return f"vec{values_len}"

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key", True, str),
    TypedDictKeyTypeVerifier("default", True, str),
))
def provider_switch(data:dict[str,Any]|Any, key:str, default:str) -> str:
    if isinstance(data, dict):
        if (output := data.get(key)) is not None:
            return output
        elif "base" in data and "spread" in data:
            return "minecraft:uniform"
        else:
            raise KeyError("type")
    else:
        return default

class ProtocolIdTypedDict(TypedDict):
    protocol_id: Required[int]

@component_function(no_arguments=True)
def registries_simplify(data:dict[str,ProtocolIdTypedDict]) -> list[str]:
    return list(data.keys())

@component_function(no_arguments=True)
def remove_minecraft_prefix(data:SCon[str]) -> str:
    return data.data.removeprefix("minecraft:")

@component_function(no_arguments=True)
def structure_jigsaw_switch(data:dict[str,Any]) -> Literal["old", "new"]:
    return "old" if "value" in data else "new"

@component_function(no_arguments=True)
def textures_split_lines(data:list[str]|str) -> list[str]:
    if isinstance(data, str):
        return data.splitlines()
    else:
        return data
