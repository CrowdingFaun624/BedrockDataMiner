from typing import Any

import Utilities.File as File

__all__ = ["normalize_sound_definitions"]

def normalize_sound_definitions(data:dict[str,File.File[dict[str,Any]]]) -> File.FakeFile[dict[str,dict[str,Any]]]:
    # resource packs are always the top level.
    # inside resource pack, it's sometimes wrapped in {"sound_definitions": dict_of_sound_events}
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, sound_definitions_file in data.items():
        file_hashes.append(hash(sound_definitions_file))
        sound_definitions = sound_definitions_file.data
        if "sound_definitions" in sound_definitions:
            sound_definitions:dict[str,Any] = sound_definitions["sound_definitions"]
        for event_name, event_data in sound_definitions.items():
            if event_name not in output:
                output[event_name] = {}
            output[event_name][pack_name] = event_data
    return File.FakeFile("combined_sound_definitions_file", output, hash(tuple(file_hashes)))
