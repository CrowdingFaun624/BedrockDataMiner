from typing import Any

__all__ = ["sound_definitions_make_strings_to_dict"]

def sound_definitions_make_strings_to_dict(data:Any) -> Any:
    if isinstance(data, str):
        return {"name": data}
