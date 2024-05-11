import json
from typing import Any, TypedDict
from typing_extensions import NotRequired, Required

import Downloader.Manager as Manager

class FileTypeTypedDict(TypedDict):
    allowed_managers: Required[list[str]]
    must_exist: Required[bool]


class VersionFilesTypedDict(TypedDict):
    files_types: Required[dict[str,FileTypeTypedDict]]
    managers: Required[dict[str,Manager.ManagerTypedDict]]


class FileType():

    def __init__(self, file_type_name:str, file_type_data:FileTypeTypedDict, managers:dict[str,Manager.Manager]) -> None:
        self.name = file_type_name
        self.allowed_managers:list[Manager.Manager] = self.get_allowed_managers(file_type_data["allowed_managers"], managers)
        self.must_exist = file_type_data["must_exist"]

    def get_allowed_managers(self, allowed_managers_str:list[str], managers:dict[str,Manager.Manager]) -> list[Manager.Manager]:
        output:list[Manager.Manager] = []
        for allowed_manager_str in allowed_managers_str:
            manager = managers.get(allowed_manager_str, None)
            if manager is None:
                raise ValueError("Unrecognized manager \"%s\" in file type \"%s\"!" % (allowed_manager_str, self.name))
            output.append(manager)
        return output

class VersionFiles():

    def __init__(self, data:VersionFilesTypedDict) -> None:
        self.managers = {manager_name: Manager.Manager(manager_name, manager_data) for manager_name, manager_data in data["managers"].items()}
        self.file_types = {file_type_name: FileType(file_type_name, file_type_data, self.managers) for file_type_name, file_type_data in data["files_types"].items()}
