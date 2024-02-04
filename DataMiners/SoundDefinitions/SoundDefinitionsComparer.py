from typing import TYPE_CHECKING

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MySoundDefinitionsJson, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedSoundDefinitionsJson:
    def fix_properties(properties:dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]) -> dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]:
        '''Removes illegal created by bugs.'''
        for resource_pack_name, resource_pack_properties in properties.items():
            if "pitch" in resource_pack_properties: del resource_pack_properties["pitch"] # MCPE-153558
            if "volume" in resource_pack_properties: del resource_pack_properties["volume"] # MCPE-178265
            for sound in resource_pack_properties["sounds"]:
                if isinstance(sound, dict):
                    if "pitch:" in sound: del sound["pitch:"] # MCPE-153561
        return properties
    def make_sounds_dict(properties:dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]) -> dict[str,DataMinerTyping.NormalizedSoundDefinitionsJsonSoundEventTypedDict]:
        for resource_pack_name, resource_pack_properties in properties.items():
            sounds:dict[str,DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict] = {}
            for sound in resource_pack_properties["sounds"]:
                if isinstance(sound, str):
                    sounds[sound] = {}
                else:
                    sounds[sound["name"]] = sound
                    del sounds[sound["name"]]["name"]
            resource_pack_properties["sounds"] = sounds
        return properties
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dataminers["resource_packs"].get_data_file(version, True)
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}] # hardcoded in sound definitions dataminer if there are no resource packs
    return {sound_event_name: CollapseResourcePacks.collapse_resource_packs(make_sounds_dict(fix_properties(sound_event_properties)), resource_packs, version.name) for sound_event_name, sound_event_properties in data.items()}

def resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundEventTypedDict) -> DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict:
    output = value.copy()
    del value["defined_in"]
    return output

def sound_comparison_move_function(key:str, value:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict) -> str:
    return key.split("/")[-1]

comparer = ComparerImporter.load_from_file("sound_definitions", {
    "normalize": normalize,
    "resource_pack_comparison_move_function": resource_pack_comparison_move_function,
    "sound_comparison_move_function": sound_comparison_move_function
    })
