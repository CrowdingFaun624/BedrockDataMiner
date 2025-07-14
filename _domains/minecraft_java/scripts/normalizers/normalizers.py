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
def density_function_switch(data:float|dict) -> str:
    if isinstance(data, float):
        return "constant_shorthand"
    else:
        assert not isinstance(data, int) # ?????? why is this necessary??
        return data["type"]

@component_function(no_arguments=True)
def font_providers_normalize_skip(data:str|list[str]) -> list[str]|None:
    if isinstance(data, str):
        return list(data)

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, str),
))
def open_file[A](data:A|File[A], serializer:str) -> A|None:
    if isinstance(data, File):
        return data.read(domain.script_referenceable.get(serializer))

class PacksOutputTypedDict(TypedDict):
    packs: list[str]
    namespaces:list[str]

@component_function(no_arguments=True)
def packs_normalizer(data:PacksInputTypedDict) -> PacksOutputTypedDict:
    return {"packs": list(data["packs"].keys()), "namespaces": list(data["packs"].keys())}

@component_function(no_arguments=True)
def post_effect_switch(data:dict[str,Any]) -> Literal["number", "matrix"]:
    if "name" in data:
        return "matrix"
    else:
        return "number"

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
def textures_split_lines(data:list[str]|str) -> list[str]|None:
    if isinstance(data, str):
        return data.splitlines()
