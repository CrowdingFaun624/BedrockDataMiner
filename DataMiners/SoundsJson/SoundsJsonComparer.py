from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MySoundsJsonTypedDict, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.MySoundsJsonTypedDict:
    def normalize_sound_collection(sound_collection_name:str, sound_collection:DataMinerTyping.ResourcePackSoundsJsonSoundCollectionTypedDict, is_interactive_entites:bool=False) -> dict[str, dict[str, DataMinerTyping.SoundsJsonSoundTypedDict]]:
        if not all(key in ("volume", "pitch", "events") for key in sound_collection.keys()):
            raise KeyError("A key in `sound_collection` (name \"%s\") is not equal to \"volume\", \"pitch\", or \"events\": %s" % (sound_collection_name, list(sound_collection.keys())))
        if "events" not in sound_collection:
            raise KeyError("Key \"events\" is not in `sound_collection` (name \"%s\"): %s" % (sound_collection_name, list(sound_collection.keys())))
        
        if "volume" in sound_collection: sound_collection["volume"] = CollapseResourcePacks.collapse_resource_packs(sound_collection["volume"], resource_packs, version.name, False)
        if "pitch" in sound_collection: sound_collection["pitch"] = CollapseResourcePacks.collapse_resource_packs(sound_collection["pitch"], resource_packs, version.name, False)

        for sound_name, sound_properties in sound_collection["events"].items():

            # bug fixes.
            resource_packs_to_delete:list[str] = []
            for resource_pack_name, resource_pack_properties in sound_properties.items():
                # print(sound_collection_name, resource_pack_name, not isinstance(resource_pack_properties, str), "sound" in resource_pack_properties, (is_interactive_entites and "default" in resource_pack_properties), resource_pack_properties)
                if not isinstance(resource_pack_properties, str):
                    if not ("sound" in resource_pack_properties or (is_interactive_entites and "default" in resource_pack_properties)):
                        resource_packs_to_delete.append(resource_pack_name)
                    if not is_interactive_entites:
                        if "sounds" in resource_pack_properties: # moves key "sounds" to "sound". It occurs a whole lot and for a long time, so it's gotta be on purpose.
                            assert "sound" not in resource_pack_properties # TODO: find out if "sounds" is actually a valid key.
                            resource_pack_properties["sound"] = resource_pack_properties["sounds"]
                            del resource_pack_properties["sounds"]
                        for key in [key for key in resource_pack_properties.keys() if key not in ("sound", "volume", "pitch")]:
                            del resource_pack_properties[key]
            for resource_pack_name in resource_packs_to_delete:
                del sound_collection["events"][sound_name][resource_pack_name]

            sound_collection["events"][sound_name] = CollapseResourcePacks.collapse_resource_packs(sound_properties, resource_packs, version.name, False)

    def normalize_sound_collections(sound_collections:dict[str,DataMinerTyping.ResourcePackSoundsJsonSoundCollectionTypedDict], is_interactive_entites:bool=False) -> dict[str,DataMinerTyping.ResourcePackSoundsJsonSoundCollectionTypedDict]:
        if "defaults" in sound_collections and len(sound_collections["defaults"]) == 0:
            del sound_collections["defaults"]
        for sound_collection_name, sound_collection_properties in sound_collections.items():
            if len(sound_collection_properties) == 0:
                raise ValueError("Sound collection \"%s\"'s properties are empty!" % (sound_collection_name))
            normalize_sound_collection(sound_collection_name, sound_collection_properties, is_interactive_entites)

    assert set(data.keys()) == {"individual_event_sounds", "block_sounds", "interactive_block_sounds", "entity_sounds", "interactive_entity_sounds"}
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dataminers["resource_packs"].get_data_file(version)
    normalize_sound_collection("individual_sound_events", data["individual_event_sounds"])
    normalize_sound_collections(data["block_sounds"])
    normalize_sound_collections(data["interactive_block_sounds"])
    normalize_sound_collections(data["entity_sounds"])
    normalize_sound_collections(data["interactive_entity_sounds"], is_interactive_entites=True)
    return data

def make_pitch_volume_list_comparer(name:str) -> Comparer.ListComparerSection:
    return Comparer.ListComparerSection(
        name=name,
        types=(float, int),
        comparer=None,
        print_flat=True,
        ordered=True
    )

def make_sound_collection_comparer(is_flat:bool, is_interactive_entities:bool=False) -> Comparer.DictComparerSection:
    key_types = ("events",) if is_flat else ("events", "volume", "pitch")

    if is_interactive_entities:
        sound_comparers = Comparer.DictComparerSection(
            name="case",
            key_types=(str,),
            value_types=(str, dict),
            comparer = None,
            detect_key_moves=True
        )
    else:
        sound_comparers = [
            (lambda key, value: isinstance(value, str), None),
            (lambda key, value: isinstance(value, dict), Comparer.TypedDictComparerSection(
                name="sound",
                types=[
                    ("sound", str, None),
                    ("pitch", (float, int, list), [
                        (lambda key, value: isinstance(value, (float, int)), None),
                        (lambda key, value: isinstance(value, list), make_pitch_volume_list_comparer("pitch"))
                    ]),
                    ("volume", (float, int, list), [
                        (lambda key, value: isinstance(value, (float, int)), None),
                        (lambda key, value: isinstance(value, list), make_pitch_volume_list_comparer("volume"))
                    ])
                ]
            ))
        ]

    return Comparer.DictComparerSection(
        name="property",
        key_types=lambda key, value: key in key_types,
        value_types=(dict,),
        comparer=[
            ("events", Comparer.DictComparerSection(
                name="event",
                key_types=(str,),
                value_types=(dict,),
                detect_key_moves=True,
                comparer=Comparer.DictComparerSection(
                    name="resource pack",
                    key_types=(str,),
                    value_types=(str, dict),
                    detect_key_moves=True, # no defined_in to deal with
                    comparer=sound_comparers
                )
            )),
            ("volume", Comparer.DictComparerSection(
                name="resource pack",
                key_types=(str,),
                value_types=(float, int, list),
                comparer=[
                    (lambda key, value: isinstance(value, (float, int)), None),
                    (lambda key, value: isinstance(value, list), make_pitch_volume_list_comparer("volume"))
                ]
            )),
            ("pitch", Comparer.DictComparerSection(
                name="resource pack",
                key_types=(str,),
                value_types=(float, int, list),
                comparer=[
                    (lambda key, value: isinstance(value, (float, int)), None),
                    (lambda key, value: isinstance(value, list), make_pitch_volume_list_comparer("pitch"))
                ]
            ))
        ]
    )    

def make_sound_collections_comparer(name:str, is_flat:bool, is_interactive_entities:bool=False) -> Comparer.DictComparerSection:
    return Comparer.DictComparerSection(
        name=name,
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=True,
        comparer=make_sound_collection_comparer(is_flat, is_interactive_entities)
    )

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.TypedDictComparerSection(
        name="category",
        types=[
            ("individual_event_sounds", dict, make_sound_collection_comparer(True)),
            ("block_sounds", dict, make_sound_collections_comparer("block", False)),
            ("interactive_block_sounds", dict, make_sound_collections_comparer("interactive block", False)),
            ("entity_sounds", dict, make_sound_collections_comparer("entity", False)),
            ("interactive_entity_sounds", dict, make_sound_collections_comparer("interactive entity", False, is_interactive_entities=True))
        ]
    ),
)
