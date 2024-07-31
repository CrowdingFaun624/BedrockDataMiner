from typing import Any, TypedDict

__all__ = ["animation_controllers_fix_old"]

input_typed_dict = TypedDict("input_typed_dict", defined_in=list[str])
output_typed_dict = TypedDict("output_typed_dict", defined_in=list[str], animation_controllers=Any)

def animation_controllers_fix_old(data:input_typed_dict|output_typed_dict) -> output_typed_dict|None:
    if "animation_controllers" in data:
        return None
    output:output_typed_dict = {"defined_in": data["defined_in"], "animation_controllers": data}
    del output["animation_controllers"]["defined_in"]
    return output
