import Comparison.ComparerImporter as ComparerImporter
import DataMiners.DataMinerTyping as DataMinerTyping

def remove_obj(data:DataMinerTyping.SoundFilesTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    if "_obj" in data:
        del data["_obj"]

def sound_file_comparison_move_function(key:str, value:dict[str,DataMinerTyping.NormalizedSoundFilesTypedDict]) -> dict[str,str]:
    return {internal_sound_file_name: internal_sound_file_properties["sha1_hash"] for internal_sound_file_name, internal_sound_file_properties in value.items()}

comparer = ComparerImporter.load_from_file("sound_files", {
    "remove_obj": remove_obj,
    "sound_file_comparison_move_function": sound_file_comparison_move_function,
    "internal_sound_file_comparison_move_function": lambda key, value: value["sha1_hash"]
})
