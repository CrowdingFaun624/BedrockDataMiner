from typing import Any

import Utilities.File as File

__all__ = ["normalize_sounds_json"]

def normalize_sounds_json(data:dict[str,File.File[dict[str,Any]]]) -> Any:
    # resource packs are always the top level.
    # inside resource pack, it's sometimes wrapped in {"sound_definitions": dict_of_sound_events}
    output:dict[str,dict[str,Any]] = {}
    for pack_name, sound_definitions_file in data.items():
        sound_definitions = sound_definitions_file.read()
        if "sound_definitions" in sound_definitions:
            sound_definitions:dict[str,Any] = sound_definitions["sound_definitions"]
        for event_name, event_data in sound_definitions.items():
            if event_name not in output:
                output[event_name] = {}
            output[event_name][pack_name] = event_data
    return output
