from typing import Any

__all__ = ["sounds_json_make_strings_to_dict"]

def sounds_json_make_strings_to_dict(data:Any) -> Any:
    if isinstance(data, str):
        return {"sound": data}
