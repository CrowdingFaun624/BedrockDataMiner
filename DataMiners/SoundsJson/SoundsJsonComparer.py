import Comparison.ComparerImporter as ComparerImporter
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

def remove_bad_events(data:dict[str,str|DataMinerTyping.SoundsJsonSoundTypedDict], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    events_to_delete:list[str] = []
    for event_name, event_properties in data.items():
        if isinstance(event_properties, str): continue
        if "sound" not in event_properties and "sounds" not in event_properties:
            events_to_delete.append(event_name)
    for event_to_delete in events_to_delete:
        del data[event_to_delete]

def remove_bad_interactive_entity_events(data:dict[str,dict[str,str]], dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    events_to_delete:list[str] = []
    for event_name, event_properties in data.items():
        if isinstance(event_properties, str): continue
        if "default" not in event_properties:
            events_to_delete.append(event_name)
    for event_to_delete in events_to_delete:
        del data[event_to_delete]

def fix_sounds(data:DataMinerTyping.SoundsJsonSoundTypedDict, dependencies:DataMinerTyping.DependenciesTypedDict) -> None:
    '''moves key "sounds" to "sound". It occurs a whole lot and for a long time, so it's gotta be on purpose.'''
    # TODO: find out if "sounds" is actually a valid key.
    for key in [key for key in data.keys() if key not in ("sound", "sounds", "volume", "pitch")]:
        del data[key]
    if "sounds" in data:
        assert "sound" not in data or data["sound"] == data["sounds"]
        data["sound"] = data["sounds"]
        del data["sounds"]

comparer = ComparerImporter.load_from_file("sounds_json", {
    "collapse_resource_packs": CollapseResourcePacks.make_interface(has_defined_in_key=True),
    "collapse_resource_packs_flat": CollapseResourcePacks.make_interface(has_defined_in_key=False),
    "fix_sounds": fix_sounds,
    "remove_bad_events": remove_bad_events,
    "remove_bad_interactive_entity_events": remove_bad_interactive_entity_events,
    "sound_collections_comparison_move_function": lambda key, value: None if len(value) == 0 else value,
})
