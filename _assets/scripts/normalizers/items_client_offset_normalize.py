from typing import Required, TypedDict

import Utilities.File as File

__all__ = ["items_client_offset_normalize"]

class ItemTypedDict(TypedDict):
    VR_hand_controller_position_adjust: Required[list[float]]
    VR_hand_controller_rotation_adjust: Required[list[float]]
    VR_hand_controller_scale: Required[float]

class FileTypedDict(TypedDict):
    render_offsets: Required[dict[str,ItemTypedDict]]

def items_client_offset_normalize(data:dict[str,File.File[FileTypedDict]]) -> File.FakeFile[dict[str,dict[str,ItemTypedDict]]]:
    output:dict[str,dict[str,ItemTypedDict]] = {}
    file_hashes:list[int] = []
    for resource_pack_name, file in data.items():
        file_data = file.data
        file_hashes.append(hash(file))
        output[resource_pack_name] = file_data["render_offsets"]
    return File.FakeFile("combined_items_client_offset_file", output, hash(tuple(file_hashes)))
