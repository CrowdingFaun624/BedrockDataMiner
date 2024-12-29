from typing import Any, TypedDict

__all__ = ["remove_format_version"]

class OldTypedDict(TypedDict):
    format_version: str
    sound_definitions: dict[str,Any]

def remove_format_version(data:dict[str,OldTypedDict|dict[str,Any]]) -> None:
    for key, value in data.items():
        if "format_version" in value:
            data[key] = value["sound_definitions"]
