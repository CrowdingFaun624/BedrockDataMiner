import shutil
from typing import Literal, TypedDict

from pathlib2 import Path

import Downloader.Manager as Manager
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.StoredVersionsManager as StoredVersionsManager


class StoredManagerTypedDict(TypedDict):
    stored_name: str

class StoredManager(Manager.Manager):

    def prepare_for_install(self, file_type_arguments:StoredManagerTypedDict) -> None:
        self.apk_location = Path(str(self.location) + ".zip")
        self.name = file_type_arguments["stored_name"]
        self.file_list:list[str]|None = None
        self.index = None

    def read_index(self) -> None:
        if self.index is not None: return
        self.index = StoredVersionsManager.read_index(self.name)

    def install_all(self, destination:Path|None=None) -> None:
        if destination is None: destination = self.apk_location
        if not destination.exists():
            self.read_index()
            StoredVersionsManager.extract(self.name, destination, self.index)

    def get_file_list(self) -> list[str]:
        if self.file_list is None:
            self.read_index()
            if self.index is None:
                raise Exceptions.AttributeNoneError("index", self)
            self.file_list = sorted(self.index.keys())
        return self.file_list

    def file_exists(self, file_name:str) -> bool:
        self.read_index()
        if self.index is None:
            raise Exceptions.AttributeNoneError("index", self)
        return file_name in self.index

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        self.read_index()
        return StoredVersionsManager.read_file(self.name, file_name, mode, self.index)

    def all_done(self) -> None:
        if self.apk_location.exists():
            self.apk_location.unlink()
        if self.location.name == self.version.name: # self.location refers to the `client` subdirectory of the version directory.
            raise Exceptions.InvalidStateError(self.location.name, self.version.name, "These should not be the same!")
        if self.location.exists():
            shutil.rmtree(self.location)
