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

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=None,
    base_comparer_section=Comparer.DictComparerSection(
        name="sound file",
        key_types=(str,),
        value_types=(dict,),
        comparer=Comparer.DictComparerSection(
            name="internal sound file",
            key_types=(str,),
            value_types=(dict,),
            comparer=Comparer.DictComparerSection(
                name="property",
                key_types=lambda key, value: key in ("filesize", "pictures", "tags", "_subchunks", "streaminfo", "sha1_hash"),
                value_types=lambda key, value: isinstance(value, {
                    "filesize": (int,),
                    "pictures": (list,),
                    "tags": (dict,),
                    "_subchunks": (list,),
                    "streaminfo": (dict,),
                    "sha1_hash": (str,)
                }[key]),
                comparer=[
                    ("filesize", None),
                    ("pictures", Comparer.ListComparerSection(
                        name="picture",
                        types=(type(None),), # idk
                        comparer=None
                    )),
                    ("tags", Comparer.DictComparerSection(
                        name="tag type",
                        key_types=lambda key, value: key in ("comment", "encoder", "title", "tracknumber"),
                        value_types=(list,),
                        comparer=Comparer.ListComparerSection(
                            name="tag",
                            types=(str,),
                            comparer=None
                        )
                    )),
                    ("_subchunks", Comparer.ListComparerSection(
                        name="subchunk",
                        types=(type(None),), # idk
                        comparer=None
                    )),
                    ("streaminfo", Comparer.DictComparerSection(
                        name="property",
                        key_types=lambda key, value: key in ("_start", "_size", "_version", "_extension_data", "audio_format", "bit_depth", "bitrate", "channels", "duration", "max_bitrate", "min_bitrate", "nominal_bitrate", "sample_rate"),
                        value_types=lambda key, value: isinstance(value, {
                            "_start": (int,),
                            "_size": (int,),
                            "_version": (list,),
                            "_extension_data": (type(None),),
                            "audio_format": (str,),
                            "bit_depth": (int,),
                            "bitrate": (float, int),
                            "channels": (int,),
                            "duration": (float,),
                            "max_bitrate": (int,),
                            "min_bitrate": (int,),
                            "nominal_bitrate": (int,),
                            "sample_rate": (int),
                        }[key]),
                        comparer=[
                            ("_start", None),
                            ("_size", None),
                            ("_version", Comparer.ListComparerSection(
                                name="version number",
                                types=(int,),
                                comparer=None,
                                print_flat=True
                            )),
                            ("_extension_data", None),
                            ("audio_format", None),
                            ("bit_depth", None),
                            ("bitrate", None),
                            ("channels", None),
                            ("duration", None),
                            ("max_bitrate", None),
                            ("min_bitrate", None),
                            ("nominal_bitrate", None),
                            ("sample_rate", None)
                        ]
                    )),
                    ("sha1_hash", None)
                ]
            )
        )
    )
)
