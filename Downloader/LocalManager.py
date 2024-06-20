import os
from types import ModuleType
from typing import Any, Literal, TypedDict

import pathlib2
from pathlib2 import Path

import Downloader.Manager as Manager
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller


class LocalManagerTypedDict(TypedDict):
    file_path: str

class LocalManager(Manager.Manager):

    def get_directory_base(self, file_type_arguments:dict[str,Any], os:ModuleType, pathlib2:ModuleType) -> str:
        ...

    def prepare_for_install(self, file_type_arguments:dict[str,Any]) -> None:
        self.file_list:list[str]|None = None
        self.directory_base = Path(self.get_directory_base(file_type_arguments, os, pathlib2))
        if not self.directory_base.exists():
            raise Exceptions.ManagerFailureError(self, "Given file \"%s\" does not exist!" % (self.directory_base,))

    def install_all(self, destination:Path|None=None) -> None:
        pass # There is no need to do anything. All of the files are already there.

    def get_files_in(self, parent:str) -> list[str]:
        return [file for file in self.get_file_list() if file.startswith(parent)]

    def get_file_list(self, path:Path|None=None) -> list[str]:
        if path is None:
            if self.file_list is None:
                strip_string = self.directory_base.as_posix() + "/"
                self.file_list = [
                    file_path.replace(strip_string, "", 1)
                    for file_path in self.get_file_list(self.directory_base)
                ]
            return self.file_list
        else:
            output:list[str] = []
            for subpath in path.iterdir():
                if subpath.is_file():
                    output.append(subpath.as_posix())
                elif subpath.is_dir():
                    output.extend(self.get_file_list(subpath))
            return output

    def file_exists(self, file_name:str) -> bool:
        return self.directory_base.joinpath(file_name).exists()

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        full_path = self.directory_base.joinpath(file_name)
        with open(full_path, "r" + mode) as f:
            return f.read()

    def get_file(self, file_name:str, mode:Literal["b","t"]="b") -> FileManager.FilePromise:
        full_path = self.directory_base.joinpath(file_name)
        return FileManager.FilePromise(FunctionCaller(open, [full_path, "r" + mode]), file_name.split("/")[-1], mode)

    def all_done(self) -> None:
        pass # There is no need to do anything. All of the files are where they should be.
