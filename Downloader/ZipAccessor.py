import zipfile
from typing import Any, TypedDict

import Downloader.DirectoryAccessor as DirectoryAccessor
import Downloader.FileAccessor as FileAccessor


class LinkedAccessorsTypedDict(TypedDict):
    file: FileAccessor.FileAccessor

class ZipAccessor(DirectoryAccessor.DirectoryAccessor):

    linked_accessors = {"file": FileAccessor.FileAccessor}

    def prepare_for_install(self, instance_arguments: dict[str, Any], class_arguments: dict[str, Any], propagated_arguments:dict[str,Any], linked_accessors:LinkedAccessorsTypedDict) -> None:
        self.file_accessor = linked_accessors["file"]

        self._zip_file:zipfile.ZipFile|None = None
        self._file_list:list[str]|None = None
        self._file_set:set[str]|None = None

    @property
    def zip_file(self) -> zipfile.ZipFile:
        if self._zip_file is None:
            self._zip_file = zipfile.ZipFile(self.file_accessor.open())
        return self._zip_file

    @property
    def file_list(self) -> list[str]:
        if self._file_list is None:
            self._file_list = sorted(file.filename for file in self.zip_file.filelist)
        return self._file_list

    @property
    def file_set(self) -> set[str]:
        if self._file_set is None:
            self._file_set = set(self.file_list)
        return self._file_set

    def file_exists(self, file_name:str) -> bool:
        return file_name in self.file_set

    def read(self, file_name:str) -> bytes:
        return self.zip_file.read(file_name)
