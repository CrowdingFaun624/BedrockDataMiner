from typing import Any

__all__ = ["render_controllers_fix_old"]

def render_controllers_fix_old(data:Any) -> Any|None:
    if "render_controllers" in data:
        return None
    output = {"render_controllers": data}
    return output
