from typing import Any, BinaryIO, TypedDict

from Downloader.DirectoryAccessor import DirectoryAccessor
from Downloader.FileAccessor import FileAccessor
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class LinkedAccessorsTypedDict(TypedDict):
    directory: DirectoryAccessor

class InstanceArgumentsTypedDict(TypedDict):
    file_name: str

class SingleDirectoryFileAccessor(FileAccessor):

    instance_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("file_name", True, str),
    )
    linked_accessor_types = {"directory": DirectoryAccessor}

    __slots__ = (
        "directory_accessor",
        "file_name",
    )

    def prepare_for_install(self, instance_arguments: InstanceArgumentsTypedDict, class_arguments: dict[str, Any], linked_accessors: LinkedAccessorsTypedDict) -> None:
        self.file_name = instance_arguments["file_name"]
        self.directory_accessor = linked_accessors["directory"]

    def read(self) -> bytes:
        return self.directory_accessor.read(self.file_name)

    def open(self) -> BinaryIO:
        return self.directory_accessor.open(self.file_name)
