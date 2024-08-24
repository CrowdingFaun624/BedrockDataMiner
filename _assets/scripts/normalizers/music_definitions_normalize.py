from typing import Any

import Utilities.File as File

__all__ = ["music_definitions_normalize"]

def music_definitions_normalize(data:dict[str,File.File[dict[str,Any]]]) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = {}
    for pack_name, music_definitions_file in data.items():
        music_definitions = music_definitions_file.read()
        for environment_name, environment_data in music_definitions.items():
            if environment_name not in output:
                output[environment_name] = {}
            output[environment_name][pack_name] = environment_data
    return output
