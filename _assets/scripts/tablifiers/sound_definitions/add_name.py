from typing import Any

__all__ = ["add_name"]

def add_name(data:dict[str,dict[str,Any]]) -> None:
    defined_in = data.pop("defined_in", None)
    for key, value in data.items():
        value["name"] = key
        if defined_in is not None:
            value["defined_in"] = defined_in
