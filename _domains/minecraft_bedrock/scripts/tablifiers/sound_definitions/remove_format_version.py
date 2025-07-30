from typing import Any, TypedDict

from Component.ComponentFunctions import component_function


class OldTypedDict(TypedDict):
    format_version: str
    sound_definitions: dict[str,Any]

@component_function()
def remove_format_version(data:dict[str,OldTypedDict|dict[str,Any]]) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = {}
    for key, value in data.items():
        if "format_version" in value:
            output[key] = value["sound_definitions"]
        else:
            output[key] = value
    return output
