from typing import TypedDict

import Downloader.Manager as Manager
import Utilities.Cache as Cache
import Utilities.FileStorageManager as FileStorageManager
import Version.Version as Version


class StoredManagerTypedDict(TypedDict):
    stored_name: str

class StoredIndex(Cache.LinesCache[dict[str,tuple[str,bool]],None]):

    can_be_written = False

    def __init__(self, version:Version.Version) -> None:
        super().__init__(version.get_version_directory().joinpath("index.txt"))
        if not self.path.exists():
            print(version.name)

    def deserialize(self, data: bytes) -> dict[str,tuple[str,bool]]:
        return {line[43:]: (line[:40], bool(int(line[41]))) for line in data.decode("UTF8").split("\n")}

class StoredManager(Manager.Manager):

    def prepare_for_install(self, file_type_arguments:StoredManagerTypedDict) -> None:
        self.name = file_type_arguments["stored_name"]
        self.file_list:list[str]|None = None
        self.index = StoredIndex(self.version)

    def get_file_list(self) -> list[str]:
        if self.file_list is None:
            self.file_list = sorted(self.index.get().keys())
        return self.file_list

    def file_exists(self, file_name:str) -> bool:
        return file_name in self.index.get()

    def read(self, file_name:str) -> bytes:
        return FileStorageManager.read_archived(self.index.get()[file_name][0])

    def all_done(self) -> None:
        self.index.forget()
        self.file_list = None
