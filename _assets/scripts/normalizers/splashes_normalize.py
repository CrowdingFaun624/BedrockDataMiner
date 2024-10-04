from typing import TypedDict

import Utilities.File as File

__all__ = ["splashes_normalize"]

class SplashesTypedDict(TypedDict):
    splashes: list[str]

def splashes_normalize(data:dict[str,File.File[SplashesTypedDict]]) -> File.FakeFile[dict[str,list[str]]]:
    output:dict[str,list[str]] = {}
    file_hashes:list[int] = []
    for pack_name, splashes_file in data.items():
        splashes = splashes_file.data
        file_hashes.append(hash(splashes_file))
        if set(splashes.keys()) != {"splashes"}:
            raise KeyError("Keys [%s] aren't recognized!" % (", ".join(key for key in splashes if key != "splashes")))
        output[pack_name] = splashes["splashes"]
    return File.FakeFile("combined_splashes_file", output, hash(tuple(file_hashes)))
