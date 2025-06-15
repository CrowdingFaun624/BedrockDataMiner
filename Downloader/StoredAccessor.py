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
        "index",
    )

    def prepare_for_install(self, instance_arguments:dict[str,Any], class_arguments:dict[str,Any], propagated_arguments:dict[str,Any], linked_accessors:dict[str,"Accessor"]) -> None:
        self._file_list:list[str]|None = None
        self.index = StoredIndex(self.version)

    @property
    def file_list(self) -> Sequence[str]:
        if self._file_list is None:
            output = self._file_list = sorted(self.index.get().keys())
        if self.constrained_memory:
            self._file_list = None
        return output

    def file_exists(self, file_name:str) -> bool:
        output = file_name in self.index.get()
        if self.constrained_memory:
            self.index.forget()
        return output

    def read(self, file_name:str) -> bytes:
        output = read_archived(self.index.get()[file_name][0])
        if self.constrained_memory:
            self.index.forget()
        return output

    def open(self, file_name:str) -> BinaryIO:
        return io.BytesIO(self.read(file_name))

    def close(self) -> None:
        super().close()
        self._file_list = None

    def constrain_memory(self) -> None:
        super().constrain_memory()
        self.index.forget()
        self._file_list = None

    def all_done(self) -> None:
        super().all_done()
        self.index.forget()
        self._file_list = None

    def get_referenced_files(self, referenced_files:set[int]) -> None:
        super().get_referenced_files(referenced_files)
        referenced_files.update(hash_str_to_int(item[0]) for item in self.index.get().values())
