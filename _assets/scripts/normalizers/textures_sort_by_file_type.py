from typing import Any

__all__ = ["textures_sort_by_file_type"]

def textures_sort_by_file_type(data:dict[str,str]) -> dict[str,Any]:
    output:dict[str,Any] = {}
    if "File Type" in data:
        output[data["File Type"]] = data
    output["sha1_hash"] = data.pop("sha1_hash")
    if "defined_in" in data:
        output["defined_in"] = data.pop("defined_in")
    return output
