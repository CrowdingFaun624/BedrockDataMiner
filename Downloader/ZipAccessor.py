import zipfile
from typing import Any, BinaryIO, Sequence, TypedDict

from Downloader.DirectoryAccessor import DirectoryAccessor
from Downloader.FileAccessor import FileAccessor


class LinkedAccessorsTypedDict(TypedDict):
    file: FileAccessor

class ZipAccessor(DirectoryAccessor):

    linked_accessor_types = {"file": FileAccessor}

    __slots__ = (
        "_file_list",
        "_file_set",
        "_zip_file",
        "file_accessor",
    )

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
    def file_list(self) -> Sequence[str]:
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

    def open(self, file_name: str) -> BinaryIO:
        return self.zip_file.open(file_name) # type: ignore ; why is IO[bytes] not assignable to BinaryIO?????

    def close(self) -> None:
        super().close()
        if self._zip_file is not None:
            self._zip_file.close()
            self._zip_file = None
        self._file_list = None
        self._file_set = None

    def constrain_memory(self) -> None:
        super().constrain_memory()
        self._file_list = None
        self._file_set = None
