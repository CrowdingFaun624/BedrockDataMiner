from typing import Any, TypedDict

__all__ = ["animation_controllers_fix_old"]

input_typed_dict = dict[str,Any]
output_typed_dict = TypedDict("output_typed_dict", {"animation_controllers": Any})

def animation_controllers_fix_old(data:input_typed_dict|output_typed_dict) -> output_typed_dict|None:
    if "animation_controllers" in data:
        return None
    output:output_typed_dict = {"animation_controllers": data}
    return output
