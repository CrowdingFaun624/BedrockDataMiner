import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["UnusedSoundEventsDataMiner"]

def get_new_trace(trace:list[str], new_items:list[str]|str) -> list[str]:
    new_trace = trace.copy()
    if isinstance(new_items, str):
        new_trace.append(new_items)
    else:
        new_trace.extend(new_items)
    return new_trace

def add_item_to_output(output:dict[str,list[list[str]]], sound:str, trace:list[str]) -> None:
    if sound in output:
        output[sound].append(trace)
    else:
        output[sound] = [trace]

def add_items_to_output(output:dict[str,list[list[str]]], items:dict[str,list[list[str]]]) -> None:
    for sound, traces in items.items():
        for trace in traces:
            add_item_to_output(output, sound, trace)

def get_sounds_json_collection_sound_events(sounds_json_collection:DataMinerTyping.ResourcePackSoundsJsonFlatCollectionTypedDict, trace:list[str], is_interactive_entities:bool=False) -> dict[str,list[list[str]]]:
    output:dict[str,list[list[str]]] = {}
    if "events" not in sounds_json_collection: return output
    for event_name, event_properties in sounds_json_collection["events"].items():
        for resource_pack_name, resource_pack_properties in event_properties.items():
            if is_interactive_entities:
                for case_name, case_sound in resource_pack_properties.items():
                    add_item_to_output(output, case_sound, get_new_trace(trace, [event_name, resource_pack_name]))
            elif isinstance(resource_pack_properties, str):
                add_item_to_output(output, resource_pack_properties, get_new_trace(trace, [event_name, resource_pack_name]))
            elif "sounds" in resource_pack_properties:
                add_item_to_output(output, resource_pack_properties["sounds"], get_new_trace(trace, [event_name, resource_pack_name]))
            elif "sound" in resource_pack_properties:
                add_item_to_output(output, resource_pack_properties["sound"], get_new_trace(trace, [event_name, resource_pack_name]))
    return output

def get_sounds_json_collections_sound_events(sounds_json_collections:dict[str,DataMinerTyping.ResourcePackSoundsJsonFlatCollectionTypedDict], trace:list[str], is_interactive_entities:bool=False) -> dict[str,list[list[str]]]:
    output:dict[str,list[list[str]]] = {}
    for name, sounds_json_collection in sounds_json_collections.items():
        add_items_to_output(output, get_sounds_json_collection_sound_events(sounds_json_collection, get_new_trace(trace, name), is_interactive_entities=is_interactive_entities))
    return output

def get_sounds_json_sound_events(sounds_json:DataMinerTyping.MySoundsJsonTypedDict) -> dict[str,list[list[str]]]:
    output:dict[str,list[list[str]]] = {}
    add_items_to_output(output, get_sounds_json_collection_sound_events (sounds_json["individual_event_sounds"], ["sounds.json", "individual_event_sounds"]))
    add_items_to_output(output, get_sounds_json_collections_sound_events(sounds_json["block_sounds"], ["sounds.json", "block_sounds"]))
    add_items_to_output(output, get_sounds_json_collections_sound_events(sounds_json["entity_sounds"], ["sounds.json", "entity_sounds"]))
    add_items_to_output(output, get_sounds_json_collections_sound_events(sounds_json["interactive_block_sounds"], ["sounds.json", "interactive_block_sounds"]))
    add_items_to_output(output, get_sounds_json_collections_sound_events(sounds_json["interactive_entity_sounds"], ["sounds.json", "interactive_entity_sounds"], is_interactive_entities=True))
    return output

def get_music_definitions_sound_events(music_definitions:DataMinerTyping.MyMusicDefinitions) -> dict[str,list[list[str]]]:
    output:dict[str,list[list[str]]] = {}
    for environment_name, environment_properties in music_definitions.items():
        for resource_pack_name, resource_pack_properties in environment_properties.items():
            add_item_to_output(output, resource_pack_properties["event_name"], ["music_definitions.json", environment_name, resource_pack_name])
    return output

class UnusedSoundEventsDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("use_music_definitions", "a bool", True, bool),
    )

    def initialize(self, use_music_definitions:bool) -> None:
        self.use_music_definitions = use_music_definitions

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.UnusedSoundEvents:
        sounds_json:DataMinerTyping.MySoundsJson = environment.dependency_data.get("sounds_json", self)
        sounds_json_sound_events = get_sounds_json_sound_events(sounds_json)

        sound_definitions:DataMinerTyping.SoundDefinitionsJson = environment.dependency_data.get("sound_definitions", self)
        sound_definitions_sound_events = list(sound_definitions.keys())

        if self.use_music_definitions:
            music_definitions:DataMinerTyping.MyMusicDefinitions = environment.dependency_data.get("music_definitions", self)
            music_definitions_sound_events = get_music_definitions_sound_events(music_definitions)

        all_sound_events = set(sounds_json_sound_events.keys())
        if self.use_music_definitions:
            all_sound_events.update(music_definitions_sound_events.keys())
        return sorted(sound_event for sound_event in sound_definitions_sound_events if sound_event not in all_sound_events)
