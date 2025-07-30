from typing import Any, Literal, TypedDict

from _domains.minecraft_java.scripts.dataminers.PacksDataminer import (
    OutputTypedDict as PacksInputTypedDict,
)
from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Utilities.File import File
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
def font_providers_normalize_skip(data:str|list[str]) -> list[str]:
    if isinstance(data, str):
        return list(data)
    else:
        return data

class PacksOutputTypedDict(TypedDict):
    packs: list[str]
    namespaces:list[str]

@component_function(no_arguments=True)
def packs_normalizer(data:PacksInputTypedDict) -> PacksOutputTypedDict:
    return {"packs": list(data["packs"].keys()), "namespaces": list(data["packs"].keys())}

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
        return data[key]
    else:
        return default

@component_function(no_arguments=True)
def textures_split_lines(data:list[str]|str) -> list[str]:
    if isinstance(data, str):
        return data.splitlines()
    else:
        return data
