from typing import Any, TypedDict

__all__ = ["animations_fix_old"]

input_typed_dict = dict[str,Any]
output_typed_dict = TypedDict("output_typed_dict", animations=Any)

def animations_fix_old(data:input_typed_dict|output_typed_dict) -> output_typed_dict|None:
    if "animations" in data:
        return None
    output:output_typed_dict = {"animations": data}
    return output
