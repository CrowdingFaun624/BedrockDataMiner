from typing import TypedDict

import Utilities.File as File

__all__ = ["splashes_normalize"]

class SplashesTypedDict(TypedDict):
    splashes: list[str]

def splashes_normalize(data:dict[str,File.File[SplashesTypedDict]]) -> dict[str,list[str]]:
    output:dict[str,list[str]] = {}
    for pack_name, splashes_file in data.items():
        splashes = splashes_file.read()
        if set(splashes.keys()) != {"splashes"}:
            raise KeyError("Keys [%s] aren't recognized!" % (", ".join(key for key in splashes if key != "splashes")))
        output[pack_name] = splashes["splashes"]
    return output
