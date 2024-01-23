from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.SoundFiles, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedSoundFilesTypedDict:
    def remove_obj(internal_sound_files:dict[str,DataMinerTyping.SoundFilesTypedDict]) -> dict[str,DataMinerTyping.NormalizedSoundFilesTypedDict]:
        for internal_sound_file_name, internal_sound_file_properties in internal_sound_files.items():
            del internal_sound_file_properties["_obj"]
        return internal_sound_files
    return {sound_file_name: remove_obj(sound_file_properties) for sound_file_name, sound_file_properties in data.items()}

def sound_file_comparison_move_function(key:str, value:dict[str,DataMinerTyping.NormalizedSoundFilesTypedDict]) -> dict[str,str]:
    return {internal_sound_file_name: internal_sound_file_properties["sha1_hash"] for internal_sound_file_name, internal_sound_file_properties in value.items()}

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=None,
    base_comparer_section=Comparer.DictComparerSection(
        name="sound file",
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=True,
        comparison_move_function=sound_file_comparison_move_function,
        comparer=Comparer.DictComparerSection(
            name="internal sound file",
            key_types=(str,),
            value_types=(dict,),
            detect_key_moves=True,
            comparison_move_function=lambda key, value: value["sha1_hash"],
            comparer=Comparer.TypedDictComparerSection(
                name="property",
                types=[
                    ("filesize", int, None),
                    ("pictures", list, Comparer.ListComparerSection(
                        name="picture",
                        types=(type(None),), # idk
                        comparer=None
                    )),
                    ("tags", dict, Comparer.DictComparerSection(
                        name="tag type",
                        key_types=lambda key, value: key in ("comment", "encoder", "title", "tracknumber"),
                        value_types=(list,),
                        comparer=Comparer.ListComparerSection(
                            name="tag",
                            types=(str,),
                            comparer=None
                        )
                    )),
                    ("_subchunks", list, Comparer.ListComparerSection(
                        name="subchunk",
                        types=(type(None),), # idk
                        comparer=None
                    )),
                    ("streaminfo", dict, Comparer.TypedDictComparerSection(
                        name="property",
                        types=[
                            ("_start", int, None),
                            ("_size", int, None),
                            ("_version", list, Comparer.ListComparerSection(
                                name="version number",
                                types=(int,),
                                comparer=None,
                                print_flat=True
                            )),
                            ("_extension_data", type(None), None),
                            ("audio_format", str, None),
                            ("bit_depth", int, None),
                            ("bitrate", (float, int), None),
                            ("channels", int, None),
                            ("duration", float, None),
                            ("max_bitrate", int, None),
                            ("min_bitrate", int, None),
                            ("nominal_bitrate", int, None),
                            ("sample_rate", int, None)
                        ]
                    )),
                    ("sha1_hash", str, None)
                ]
            )
        )
    )
)
