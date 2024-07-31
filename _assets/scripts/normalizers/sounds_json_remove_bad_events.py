from typing import Any

__all__ = ["sounds_json_remove_bad_events"]

def sounds_json_remove_bad_events(data:dict[str,str|dict[str,Any]], is_interactive_entity:bool) -> Any:
    events_to_delete:list[str] = [
        event_name
        for event_name, event_properties in data.items()
        if not isinstance(event_properties, str)
        if (
            "default" not in event_properties
            if is_interactive_entity
            else "sound" not in event_properties and "sounds" not in event_properties
        )
    ]
    for event in events_to_delete:
        del data[event]
