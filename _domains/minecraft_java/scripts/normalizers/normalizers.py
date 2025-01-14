from typing import Any, Literal

import _domains.minecraft_java.scripts.dataminers.PacksDataminer as PacksDataminer

__all__ = [
    "font_providers_normalize_skip",
    "packs_normalizer",
    "post_effect_switch",
]

def font_providers_normalize_skip(data:str|list[str]) -> list[str]|None:
    if isinstance(data, str):
        return list(data)

def packs_normalizer(data:list[PacksDataminer.PackTypedDict]) -> list[str]:
    return [pack["name"] for pack in data]

def post_effect_switch(data:dict[str,Any]) -> Literal["number", "matrix"]:
    if "name" in data:
        return "matrix"
    else:
        return "number"
