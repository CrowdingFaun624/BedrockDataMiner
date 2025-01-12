from typing import Any, Literal

__all__ = ["post_effect_switch"]

def post_effect_switch(data:dict[str,Any]) -> Literal["number", "matrix"]:
    if "name" in data:
        return "matrix"
    else:
        return "number"
