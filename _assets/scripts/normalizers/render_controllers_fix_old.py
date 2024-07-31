from typing import Any

__all__ = ["render_controllers_fix_old"]

def render_controllers_fix_old(data:Any) -> Any|None:
    if "render_controllers" in data:
        return None
    output = {
        "defined_in": data["defined_in"],
        "render_controllers": data,
    }
    del data["defined_in"]
    return output
