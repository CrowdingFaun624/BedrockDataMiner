from typing import Any, TypedDict

from typing_extensions import Required

import Utilities.File as File

__all__ = ["items_client_offset_normalize"]

class ItemTypedDict(TypedDict):
    VR_hand_controller_position_adjust: Required[list[float]]
    VR_hand_controller_rotation_adjust: Required[list[float]]
    VR_hand_controller_scale: Required[float]

class FileTypedDict(TypedDict):
    render_offsets: Required[dict[str,ItemTypedDict]]

def items_client_offset_normalize(data:dict[str,File.File[FileTypedDict]]) -> Any:
    output:dict[str,dict[str,ItemTypedDict]] = {}
    for resource_pack_name, file in data.items():
        file_data = file.read()
        output[resource_pack_name] = file_data["render_offsets"]
    return output
