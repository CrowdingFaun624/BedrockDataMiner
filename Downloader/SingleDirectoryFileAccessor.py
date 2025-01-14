from typing import Any, BinaryIO, TypedDict

import Downloader.DirectoryAccessor as DirectoryAccessor
import Downloader.FileAccessor as FileAccessor
import Utilities.TypeVerifier as TypeVerifier


class LinkedAccessorsTypedDict(TypedDict):
    directory: DirectoryAccessor.DirectoryAccessor

class InstanceArgumentsTypedDict(TypedDict):
    file_name: str

class SingleDirectoryFileAccessor(FileAccessor.FileAccessor):

    instance_parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", True, str),
    )
    linked_accessors = {"directory": DirectoryAccessor.DirectoryAccessor}

    __slots__ = (
        "directory_accessor",
        "file_name",
    )

    def prepare_for_install(self, instance_arguments: InstanceArgumentsTypedDict, class_arguments: dict[str, Any], propagated_arguments: dict[str, Any], linked_accessors: LinkedAccessorsTypedDict) -> None:
        self.file_name = instance_arguments["file_name"]
        self.directory_accessor = linked_accessors["directory"]

    def read(self) -> bytes:
        return self.directory_accessor.read(self.file_name)

    def open(self) -> BinaryIO:
        return self.directory_accessor.open(self.file_name)
