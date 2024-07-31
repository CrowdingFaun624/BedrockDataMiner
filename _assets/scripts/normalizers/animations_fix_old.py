from typing import Any, TypedDict

__all__ = ["animations_fix_old"]

input_typed_dict = TypedDict("input_typed_dict", defined_in=list[str])
output_typed_dict = TypedDict("output_typed_dict", defined_in=list[str], animations=Any)

def animations_fix_old(data:input_typed_dict|output_typed_dict) -> output_typed_dict|None:
    if "animations" in data:
        return None
    output:output_typed_dict = {"defined_in": data["defined_in"], "animations": data}
    del output["animations"]["defined_in"]
    return output
