import json
from typing import Any, TypedDict

from typing_extensions import NotRequired, Required

import Utilities.FileManager as FileManager


class AutoAssignTypedDict(TypedDict):
    accessor: Required[str]
    parameters: Required[dict[str,Any]]

class FileTypeTypedDict(TypedDict):
    allowed_accessors: Required[list[str]]
    auto_assign: NotRequired[AutoAssignTypedDict]
    install_location: Required[str]
    must_exist: Required[bool]

class VersionFileType():

    def __init__(self, name:str, data:FileTypeTypedDict) -> None:
        self.name = name
        self.allowed_accessors = data["allowed_accessors"]
        self.install_location = data["install_location"]
        self.must_exist = data["must_exist"]
        self.auto_assign = data.get("auto_assign", None)
    
    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "<VersionFileType %s>" % (self.name)

def parse() -> dict[str,VersionFileType]:
    with open(FileManager.VERSION_FILE_TYPES_FILE, "rt") as f:
        data:dict[str,FileTypeTypedDict] = json.load(f)
        return {file_type_name: VersionFileType(file_type_name, file_type_data) for file_type_name, file_type_data in data.items()}

version_file_types = parse()
