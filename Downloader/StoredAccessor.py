import io
from typing import Any, BinaryIO, Sequence

from Downloader.Accessor import Accessor
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.Cache import LinesCache
from Utilities.File import hash_str_to_int
from Utilities.FileStorage import read_archived
from Version.Version import Version


class StoredIndex(LinesCache[dict[str,tuple[str,bool]],None]):

    can_be_written = False

    def __init__(self, version:Version) -> None:
        super().__init__(version.version_directory.joinpath("index.txt"))

    def deserialize(self, data: bytes) -> dict[str,tuple[str,bool]]:
        return {line[43:]: (line[:40], bool(int(line[41]))) for line in data.decode("UTF8").split("\n")}

class StoredAccessor(DirectoryAccessor):

    __slots__ = (
        "_file_list",
        "_file_set",
        "index",
    )

    def prepare_for_install(self, instance_arguments:dict[str,Any], class_arguments:dict[str,Any], propagated_arguments:dict[str,Any], linked_accessors:dict[str,"Accessor"]) -> None:
        self._file_list:list[str]|None = None
        self._file_set:set[str]|None = None
        self.index = StoredIndex(self.version)

    @property
    def file_list(self) -> Sequence[str]:
        if self._file_list is None:
            self._file_list = sorted(self.index.get().keys())
        return self._file_list

    def file_exists(self, file_name:str) -> bool:
        return file_name in self.index.get()

    def read(self, file_name:str) -> bytes:
        return read_archived(self.index.get()[file_name][0])

    def open(self, file_name:str) -> BinaryIO:
        return io.BytesIO(self.read(file_name))

    def all_done(self) -> None:
        self.index.forget()
        self._file_list = None
        self._file_set = None

    def get_referenced_files(self, get_referenced_files:set[int]) -> None:
        get_referenced_files.update(hash_str_to_int(item[0]) for item in self.index.get().values())
