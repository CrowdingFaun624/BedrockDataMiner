from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

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
    return {sound_event_name: CollapseResourcePacks.collapse_resource_packs(fix_properties(sound_event_properties), resource_packs, version.name) for sound_event_name, sound_event_properties in data.items()}

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
            comparer=Comparer.TypedDictComparerSection(
                name="property",
                types=[
                    ("category", str, None),
                    ("defined_in", list, Comparer.ListComparerSection(
                        name="resource pack",
                        types=(str,),
                        comparer=None,
                        print_flat=True,
                        ordered=False
                    )),
                    ("min_distance", (float, int), None),
                    ("max_distance", (float, int), None),
                    ("sounds", list, Comparer.ListComparerSection(
                        name="sound",
                        types=(str, dict),
                        ordered=False,
                        comparer=[
                            (lambda key, value: isinstance(value, str), None),
                            (lambda key, value: isinstance(value, dict), Comparer.TypedDictComparerSection(
                                name="property",
                                types=[
                                    ("exclude_from_pocket_platforms", bool, None),
                                    ("is3D", bool, None),
                                    ("load_on_low_memory", bool, None),
                                    ("name", str, None),
                                    ("pitch", (float, int), None),
                                    ("stream", bool, None),
                                    ("type", str, None),
                                    ("volume", (float, int), None),
                                    ("weight", int, None)
                                ]
                            ))
                        ]
                    )),
                    ("subtitle", str, None)
                ]
            )
        )
    )
)
