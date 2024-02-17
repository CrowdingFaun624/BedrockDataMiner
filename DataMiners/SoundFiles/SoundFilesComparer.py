import DataMiners.DataMinerTyping as DataMinerTyping
import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.SoundFiles, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedSoundFilesTypedDict:
    def remove_obj(internal_sound_files:dict[str,DataMinerTyping.SoundFilesTypedDict]) -> dict[str,DataMinerTyping.NormalizedSoundFilesTypedDict]:
        for internal_sound_file_name, internal_sound_file_properties in internal_sound_files.items():
            del internal_sound_file_properties["_obj"]
        return internal_sound_files
    return {sound_file_name: remove_obj(sound_file_properties) for sound_file_name, sound_file_properties in data.items()}

def sound_file_comparison_move_function(key:str, value:dict[str,DataMinerTyping.NormalizedSoundFilesTypedDict]) -> dict[str,str]:
    return {internal_sound_file_name: internal_sound_file_properties["sha1_hash"] for internal_sound_file_name, internal_sound_file_properties in value.items()}

comparer = ComparerImporter.load_from_file("sound_files", {
    "normalize": normalize,
    "sound_file_comparison_move_function": sound_file_comparison_move_function,
    "internal_sound_file_comparison_move_function": lambda key, value: value["sha1_hash"]
    })
