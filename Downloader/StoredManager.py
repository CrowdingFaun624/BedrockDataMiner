import shutil
from typing import Literal, TypedDict

from pathlib2 import Path

import Downloader.Manager as Manager
import Utilities.FileManager as FileManager
import Utilities.StoredVersionsManager as StoredVersionsManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.VersionTags as VersionTags


class StoredManagerTypedDict(TypedDict):
    stored_name: str

class StoredManager(Manager.Manager):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("stored_name", "a str", True, str),
    )

    def prepare_for_install(self, version_tags:VersionTags.VersionTags, file_type_arguments:StoredManagerTypedDict) -> None:
        self.apk_location = Path(str(self.location) + ".zip")
        self.name = file_type_arguments["stored_name"]
        self.file_list:list[str]|None = None
        self.index = None

    def read_index(self) -> None:
        if self.index is not None: return
        self.index = StoredVersionsManager.read_index(self.name)

    def install_all(self, destination:Path|None=None) -> None:

        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")

        if destination is None: destination = self.apk_location
        if not destination.exists():
            self.read_index()
            StoredVersionsManager.extract(self.name, destination, self.index)

    def get_files_in(self, parent: str) -> list[str]:
        return [file for file in self.get_file_list() if file.startswith(parent)]

    def get_file_list(self) -> list[str]:
        if self.file_list is None:
            self.read_index()
            assert self.index is not None
            self.file_list = list(self.index.keys())
        return self.file_list

    def file_exists(self, name:str) -> bool:
        self.read_index()
        assert self.index is not None
        return name in self.index

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        self.read_index()
        return StoredVersionsManager.read_file(self.name, file_name, mode, self.index)

    def get_file(self, file_name:str, mode:Literal["b","t"]="b") -> FileManager.FilePromise:
        self.read_index()
        return StoredVersionsManager.get_file(self.name, file_name, mode, self.index)

    def all_done(self) -> None:
        if self.apk_location.exists():
            self.apk_location.unlink()
        assert self.location.name != self.version.name # self.location refers to the `client` subdirectory of the version folder.
        if self.location.exists():
            shutil.rmtree(self.location)
