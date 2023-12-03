from pathlib2 import Path
from typing import IO, Iterable

import Downloader.InstallManager as InstallManager
import Utilities.StoredVersionsManager as StoredVersionsManager
import Utilities.Version as Version

class StoredManager(InstallManager.InstallManager):
    def prepare_for_install(self) -> None:
        self.name = self.version.download_link[1:]
        self.index = StoredVersionsManager.read_index(self.name)
        if not self.version.download_method is Version.DOWNLOAD_FILE:
            raise ValueError("Version \"%s\" is using a StoredManager while having a \"%s\" download type!" % (self.version.name, self.version.download_method))
    
    def install(self, file_name:str, destination:Path|None=None) -> Path:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")
        
        file_name = self.get_full_file_name(file_name)
        if destination is None:
            destination = Path(self.location.joinpath(file_name))
        StoredVersionsManager.extract_file(self.name, file_name, destination, self.index)
        return destination

    def install_all(self, destination:Path|None=None) -> None:

        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")

        if destination is None: destination = self.location
        StoredVersionsManager.extract(self.name, destination, self.index)

    def get_file_list(self) -> Iterable[str]:
        return self.index.keys()

    def read(self, file_name:str, mode:str="b") -> bytes|str:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        file_name = self.get_full_file_name(file_name)
        StoredVersionsManager.read_file(self.name, file_name, mode, self.index)
    
    def get_full_file_name(self, asset_name:str) -> str:
        return "assets/" + asset_name
    
    def get_file(self, file_name:str, mode:str="b") -> IO[bytes]:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        file_name = self.get_full_file_name(file_name)
        return StoredVersionsManager.get_file(self.name, file_name, mode, self.index)
