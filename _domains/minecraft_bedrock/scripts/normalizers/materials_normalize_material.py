from typing import Any, TypedDict, cast

__all__ = ["materials_normalize_material"]

input_typed_dict = TypedDict("input_typed_dict", {"version": str, "materials": dict[str,Any]})

output_typed_dict = TypedDict("output_typed_dict", {"materials": dict[str,Any]})

def materials_normalize_material(data:input_typed_dict|dict[str,Any]) -> output_typed_dict|None:
    if "materials" in data:
        data["version"] = cast(str, data["materials"]["version"])
        del data["materials"]["version"]
    else:
        return {"materials": data}
