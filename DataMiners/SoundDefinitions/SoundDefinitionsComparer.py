import Comparison.ComparerImporter as ComparerImporter
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

def fix_MCPE_153558(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153558
    if "pitch" in data:
        del data["pitch"]

def fix_MCPE_178265(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-178265
    if "volume" in data:
        del data["volume"]

def make_sounds_dict(data:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "sounds" in data:
        sounds:dict[str,DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict] = {}
        for sound in data["sounds"]:
            if isinstance(sound, str):
                sounds[sound] = {}
            else:
                sounds[sound["name"]] = sound
                del sound["name"]
        data["sounds"] = sounds

def fix_MCPE_153561(data:DataMinerTyping.SoundDefinitionsJsonSoundTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    # https://bugs.mojang.com/browse/MCPE-153561
    if "pitch:" in data:
        del data["pitch:"]

def resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundEventTypedDict) -> DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict:
    output = value.copy()
    del value["defined_in"]
    return output

def sound_comparison_move_function(key:str, value:DataMinerTyping.NormalizedSoundDefinitionsJsonSoundTypedDict) -> str:
    return key.split("/")[-1]

comparer = ComparerImporter.load_from_file("sound_definitions", {
    "collapse_resource_packs": CollapseResourcePacks.make_interface(),
    "fix_MCPE_153558": fix_MCPE_153558,
    "fix_MCPE_153561": fix_MCPE_153561,
    "fix_MCPE_178265": fix_MCPE_178265,
    "make_sounds_dict": make_sounds_dict,
    "resource_pack_comparison_move_function": resource_pack_comparison_move_function,
    "sound_comparison_move_function": sound_comparison_move_function,
})
