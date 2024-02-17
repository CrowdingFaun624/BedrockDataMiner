import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.MySoundsJsonTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.MySoundsJsonTypedDict:
    def normalize_sound_collection(sound_collection_name:str, sound_collection:DataMinerTyping.ResourcePackSoundsJsonSoundCollectionTypedDict, is_interactive_entites:bool=False) -> dict[str, dict[str, DataMinerTyping.SoundsJsonSoundTypedDict]]:
        if not all(key in ("volume", "pitch", "events") for key in sound_collection.keys()):
            raise KeyError("A key in `sound_collection` (name \"%s\") is not equal to \"volume\", \"pitch\", or \"events\": %s" % (sound_collection_name, list(sound_collection.keys())))
        if "events" not in sound_collection:
            raise KeyError("Key \"events\" is not in `sound_collection` (name \"%s\"): %s" % (sound_collection_name, list(sound_collection.keys())))
        
        if "volume" in sound_collection: sound_collection["volume"] = CollapseResourcePacks.collapse_resource_packs(sound_collection["volume"], resource_packs, False)
        if "pitch" in sound_collection: sound_collection["pitch"] = CollapseResourcePacks.collapse_resource_packs(sound_collection["pitch"], resource_packs, False)

        for sound_name, sound_properties in sound_collection["events"].items():

            # bug fixes.
            resource_packs_to_delete:list[str] = []
            for resource_pack_name, resource_pack_properties in sound_properties.items():
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

            sound_collection["events"][sound_name] = CollapseResourcePacks.collapse_resource_packs(sound_properties, resource_packs, False)

    def normalize_sound_collections(sound_collections:dict[str,DataMinerTyping.ResourcePackSoundsJsonSoundCollectionTypedDict], is_interactive_entites:bool=False) -> dict[str,DataMinerTyping.ResourcePackSoundsJsonSoundCollectionTypedDict]:
        if "defaults" in sound_collections and len(sound_collections["defaults"]) == 0:
            del sound_collections["defaults"]
        for sound_collection_name, sound_collection_properties in sound_collections.items():
            if len(sound_collection_properties) == 0:
                raise ValueError("Sound collection \"%s\"'s properties are empty!" % (sound_collection_name))
            normalize_sound_collection(sound_collection_name, sound_collection_properties, is_interactive_entites)

    assert set(data.keys()) == {"individual_event_sounds", "block_sounds", "interactive_block_sounds", "entity_sounds", "interactive_entity_sounds"}
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dependencies["resource_packs"]
    normalize_sound_collection("individual_sound_events", data["individual_event_sounds"])
    normalize_sound_collections(data["block_sounds"])
    normalize_sound_collections(data["interactive_block_sounds"])
    normalize_sound_collections(data["entity_sounds"])
    normalize_sound_collections(data["interactive_entity_sounds"], is_interactive_entites=True)
    return data

comparer = ComparerImporter.load_from_file("sounds_json", {
    "normalize": normalize,
    "sound_collections_comparison_move_function": lambda key, value: None if len(value) == 0 else value,
    })
