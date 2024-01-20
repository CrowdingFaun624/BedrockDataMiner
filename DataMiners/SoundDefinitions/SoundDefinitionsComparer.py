from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MySoundDefinitionsJson, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedSoundDefinitionsJson:
    def fix_properties(properties:DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict) -> DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict:
        '''Removes illegal created by bugs.'''
        for resource_pack_name, resource_pack_properties in properties.items():
            if "pitch" in resource_pack_properties: del resource_pack_properties["pitch"] # MCPE-153558
            if "volume" in resource_pack_properties: del resource_pack_properties["volume"] # MCPE-178265
            for sound in resource_pack_properties["sounds"]:
                if isinstance(sound, dict):
                    if "pitch:" in sound: del sound["pitch:"] # MCPE-153561
        return properties
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dataminers["resource_packs"].get_data_file(version, True)
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}] # hardcoded in sound definitions dataminer if there are no resource packs
    return {sound_event_name: Comparer.collapse_resource_packs(fix_properties(sound_event_properties), resource_packs, version.name) for sound_event_name, sound_event_properties in data.items()}

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="sound event",
        key_types=(str,),
        value_types=(dict,),
        comparer=Comparer.DictComparerSection(
            name="resource pack",
            key_types=(str,),
            value_types=(dict,),
            comparer=Comparer.DictComparerSection(
                name="property",
                key_types=lambda key, value: key in ("category", "defined_in", "min_distance", "max_distance", "sounds", "subtitle"),
                value_types=lambda key, value: isinstance(value, {
                    "category": (str,),
                    "defined_in": (list,), # artificial
                    "min_distance": (float, int),
                    "max_distance": (float, int),
                    "sounds": (list,),
                    "subtitle": (str,)
                }[key]),
                comparer=[
                    ("category", None),
                    ("defined_in", Comparer.ListComparerSection(
                        name="resource pack",
                        types=(str,),
                        comparer=None,
                        print_flat=True,
                        ordered=False
                    )),
                    ("min_distance", None),
                    ("max_distance", None),
                    ("sounds", Comparer.ListComparerSection(
                        name="sound",
                        types=(str, dict),
                        ordered=False,
                        comparer=[
                            (lambda key, value: isinstance(value, str), None),
                            (lambda key, value: isinstance(value, dict), Comparer.DictComparerSection(
                                name="property",
                                key_types=(str,),
                                value_types=lambda key, value: isinstance(value, {
                                    "exclude_from_pocket_platforms": (bool,), # older versions such as a0.15.0_build1
                                    "is3D": (bool,),
                                    "load_on_low_memory": (bool,),
                                    "name": (str,),
                                    "pitch": (float, int),
                                    "stream": (bool,),
                                    "type": (str,),
                                    "volume": (float, int),
                                    "weight": (int,),
                                }[key]),
                                comparer=None
                            ))
                        ]
                    )),
                    ("subtitle", None)
                ]
            )
        )
    )
)
