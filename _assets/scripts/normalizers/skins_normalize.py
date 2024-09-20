from typing import Any, TypedDict

import Utilities.File as File

__all__ = ["skins_normalize"]

class InputTypedDict(TypedDict):
    skins: list[dict[str,Any]]
    # serialize_name: str
    # localization_name: str

class OutputTypedDict(TypedDict):
    skins: list[dict[str,Any]]

def skins_normalize(data:dict[str,File.File[InputTypedDict]], other_keys:list[str]) -> OutputTypedDict:
    output:OutputTypedDict = {
        "skins": [],
    }
    for other_key in other_keys:
        output[other_key] = {}
    for pack_name, skins_file in data.items():
        skins_data = skins_file.read()
        for skin in skins_data["skins"]:
            skin["defined_in"] = pack_name
            output["skins"].append(skin)
        for other_key in other_keys:
            output[other_key][pack_name] = skins_data[other_key]
    return output
