from typing import Generator

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.NonExistentSounds.NonExistentSoundsDataMiner as NonExistentSoundsDataMiner

def strip_file_name(file_name:str, resource_packs_location:str|None) -> str|None:
    '''Removes the resource pack info and file extension from the file name.
    If it is not in the resource packs folder, return None.'''
    if resource_packs_location is not None:
        if not file_name.startswith(resource_packs_location): return None
        file_name = file_name.replace(resource_packs_location + "/", "", 1)
        resource_pack_name = file_name.split("/")[0]
        file_name = file_name.replace(resource_pack_name + "/", "", 1)
    else:
        file_name = file_name.replace("sounds/", "", 1) # in versions with sounds not in resource packs, sound_definitions.json does not include the sounds folder.
    file_extension = "." + file_name.split(".")[-1]
    assert "/" not in file_extension
    file_name = file_name.replace(file_extension, "", 1)
    assert not file_name.endswith(file_extension)
    return file_name

def get_sounds(sound_definitions:DataMinerTyping.SoundDefinitionsJson) -> Generator[tuple[str,str,str],None,None]:
    '''Yields the sound event name, the resource pack name, and the sound location. Does not yield sounds from type=event sounds.'''
    for sound_event_name, sound_event_resource_packs in sound_definitions.items():
        for resource_pack_name, resource_pack_properties in sound_event_resource_packs.items():
            for sound in resource_pack_properties["sounds"]:
                if isinstance(sound, str):
                    yield (sound_event_name, resource_pack_name, sound)
                else:
                    if "type" in sound and sound["type"] == "event":
                        continue
                    yield (sound_event_name, resource_pack_name, sound["name"])

class NonExistentSoundsDataMiner0(NonExistentSoundsDataMiner.NonExistentSoundsDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "resource_packs_location": ((str, type(None)), True),
    })

    def initialize(self, **kwargs) -> None:
        self.resource_packs_location:str|None = kwargs["resource_packs_location"]

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NonExistentSounds:
        sound_files_data = dependency_data["sound_files"]
        sound_files = {strip_file_name(sound_file, self.resource_packs_location) for sound_file in sound_files_data.keys()}
        sound_files.discard(None)
        if len(sound_files) == 0:
            raise RuntimeError("There are no sound files in a resource pack folder!")

        non_existent_sounds:dict[str,dict[str,list[str]]] = {}
        sound_definitions = dependency_data["sound_definitions"]
        total_sound_locations = 0
        total_non_existent_sound_locations = 0
        for sound_event, resource_pack, sound_location in get_sounds(sound_definitions):
            total_sound_locations += 1
            if sound_location in sound_files: continue
            total_non_existent_sound_locations += 1
            if sound_event in non_existent_sounds:
                if resource_pack in non_existent_sounds[sound_event]:
                    non_existent_sounds[sound_event][resource_pack].append(sound_location)
                else:
                    non_existent_sounds[sound_event][resource_pack] = [sound_location]
            else:
                non_existent_sounds[sound_event] = {resource_pack: [sound_location]}

        if total_sound_locations == total_non_existent_sound_locations:
            raise RuntimeError("Every sound appears to be non-existent!")

        return {key: value for key, value in sorted(non_existent_sounds.items())}
