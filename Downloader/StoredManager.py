import shutil
from typing import Iterable, Literal, TypedDict

from pathlib2 import Path

import Downloader.InstallManager as InstallManager
import Utilities.FileManager as FileManager
import Utilities.StoredVersionsManager as StoredVersionsManager
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionTags as VersionTags


class StoredManagerTypedDict(TypedDict):
    stored_name: str

class StoredManager(InstallManager.InstallManager):

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

    def install(self, file_name:str, destination:Path|None=None) -> Path:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")

        file_name = self.get_full_file_name(file_name)
        if destination is None:
            destination = Path(self.location.joinpath(file_name))
        self.read_index()
        StoredVersionsManager.extract_file(self.name, file_name, destination, self.index)
        return destination

    def install_all(self, destination:Path|None=None) -> None:

        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")

        if destination is None: destination = self.apk_location
        if not destination.exists():
            self.read_index()
            StoredVersionsManager.extract(self.name, destination, self.index)

    def get_files_in(self, parent: str) -> Iterable[str]:
        return [file for file in self.get_file_list() if file.startswith(parent)]

    def get_file_list(self) -> Iterable[str]:
        if self.file_list is None:
            strip_string = self.get_full_file_name("")
            self.read_index()
            assert self.index is not None
            self.file_list = [index.replace(strip_string, "", 1) for index in self.index.keys() if index.startswith(strip_string) and not index.endswith("/")]
        return self.file_list

    def get_full_file_list(self) -> list[str]:
        self.read_index()
        assert self.index is not None
        return list(self.index.keys())

    def file_exists(self, name:str) -> bool:
        self.read_index()
        assert self.index is not None
        return self.get_full_file_name(name) in self.index

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        file_name = self.get_full_file_name(file_name)
        self.read_index()
        return StoredVersionsManager.read_file(self.name, file_name, mode, self.index)

    def get_full_file_name(self, asset_name:str) -> str:
        return "assets/" + asset_name

    def get_file(self, file_name:str, mode:Literal["b","t"]="b", is_in_assets:bool=True) -> FileManager.FilePromise:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        if is_in_assets:
            file_name = self.get_full_file_name(file_name)
        self.read_index()
        return StoredVersionsManager.get_file(self.name, file_name, mode, self.index)

    def all_done(self) -> None:
        if self.apk_location.exists():
            self.apk_location.unlink()
        assert self.location.name != self.version.name # self.location refers to the `client` subdirectory of the version folder.
        if self.location.exists():
            shutil.rmtree(self.location)
