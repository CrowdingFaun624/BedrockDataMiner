from typing import Any, Literal

from _domains.minecraft_java.scripts.dataminers.PacksDataminer import PackTypedDict
from Component.ComponentFunctions import component_function


@component_function(no_arguments=True)
def font_providers_normalize_skip(data:str|list[str]) -> list[str]|None:
    if isinstance(data, str):
        return list(data)

@component_function(no_arguments=True)
def packs_normalizer(data:list[PackTypedDict]) -> list[str]:
    return [pack["name"] for pack in data]

@component_function(no_arguments=True)
def post_effect_switch(data:dict[str,Any]) -> Literal["number", "matrix"]:
    if "name" in data:
        return "matrix"
    else:
        return "number"
