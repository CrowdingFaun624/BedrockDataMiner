from typing import Any, BinaryIO, Sequence, TypedDict

from Downloader.DirectoryAccessor import DirectoryAccessor

__all__ = ("SubDirectoryAccessor",)

class LinkedAccessorsTypedDict(TypedDict):
    superdirectory: DirectoryAccessor

class SubDirectoryAccessor(DirectoryAccessor):

    linked_accessor_types = {"superdirectory": DirectoryAccessor}

    __slots__ = (
        "_file_list",
        "_file_set",
        "file_prepension",
        "superdirectory_accessor",
    )

    def prepare_for_install(self, instance_arguments: dict[str, Any], class_arguments: dict[str, Any], propagated_arguments:dict[str,Any], linked_accessors: LinkedAccessorsTypedDict) -> None:
        self.superdirectory_accessor = linked_accessors["superdirectory"]
        self.file_prepension:str
        if "ipa" in self.version.tags_dict:
            self.file_prepension = "Payload/minecraftpe.app/data/"
        elif "double_assets" in self.version.tags_dict:
            self.file_prepension = "assets/assets/"
        else:
            self.file_prepension = "assets/"
        self._file_list:list[str]|None = None
        self._file_set:set[str]|None = None

    def modify_file_name(self, file_name:str="") -> str:
        return self.file_prepension + file_name

    def trim_file_name(self, file_name:str) -> str:
        return file_name[len(self.file_prepension):]

    def file_exists(self, file_name:str) -> bool:
        return self.superdirectory_accessor.file_exists(self.modify_file_name(file_name))

    def get_files_in(self, parent:str) -> Sequence[str]:
        return [self.trim_file_name(file) for file in self.superdirectory_accessor.get_files_in(self.modify_file_name(parent)) if file[-1] != "/"]

    @property
    def file_list(self) -> Sequence[str]:
        if self._file_list is None:
            self._file_list = [self.trim_file_name(file) for file in self.superdirectory_accessor.get_files_in(self.modify_file_name()) if file[-1] != "/"]
        return self._file_list

    def read(self, file_name:str) -> bytes:
        return self.superdirectory_accessor.read(self.modify_file_name(file_name))

    def open(self, file_name) -> BinaryIO:
        return self.superdirectory_accessor.open(self.modify_file_name(file_name))
