from typing import IO, Iterable, TYPE_CHECKING
from pathlib2 import Path
import requests
import time
from urllib.parse import urlparse
import zipfile
import uuid

import Downloader.InstallManager as InstallManager
import Utilities.FileManager as FileManager
import Utilities.VersionTags as VersionTags

if TYPE_CHECKING:
    import Utilities.Version as Version

CONNECTION_LIMITS:dict[str,int] = {}
CONNECTION_LIMITS_DEFAULT = 1

class DownloadManager(InstallManager.InstallManager):
    current_open_connections:dict[str,list[requests.Request]] = {}

    def prepare_for_install(self) -> None:
        self.apk_location = Path(str(self.location) + ".zip")
        self.url = None
        self.installed = False
        self.installing = False
        self.zip_file = None
        self.file_list = None

        self.url = self.version.download_link
        self.domain = urlparse(self.url).netloc
        if self.domain not in self.current_open_connections:
            self.current_open_connections[self.domain] = 0
        self.connection_limit = CONNECTION_LIMITS[self.domain] if self.domain in CONNECTION_LIMITS else CONNECTION_LIMITS_DEFAULT
        self.set_file_prepension()

    def set_file_prepension(self) -> None:
        tags = self.version.tags
        if VersionTags.IPA in tags:
            prepend = "Payload/minecraftpe.app/data"
        else:
            if VersionTags.DOUBLE_ASSETS in self.version.tags:
                prepend = "assets/assets/"
            else:
                prepend = "assets/"
        self.file_prepension = prepend

    def get_full_file_name(self, asset_name:str) -> str:
        return self.file_prepension + asset_name

    def install(self, file_name:str, destination:Path|None=None) -> Path:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")
        
        if not self.installed:
            self.install_all()
        file_name = self.get_full_file_name(file_name)
        member = self.members[file_name]
        if destination is not None:
            name_carry = member.filename
            member.filename = destination.name
            self.zip_file.extract(file_name, destination.parents[0])
            member.filename = name_carry
            return destination
        else:
            self.zip_file.extract(file_name, self.location)
            return Path(self.location.joinpath(file_name))

    def get_file_list(self) -> Iterable[str]:
        if not self.installed:
            self.install_all()
        strip_string = self.get_full_file_name("")
        if self.file_list is None:
            self.file_list = [file.filename.replace(strip_string, "", 1) for file in self.zip_file.filelist]
        return self.file_list

    def file_exists(self, name:str) -> bool:
        if not self.installed:
            self.install_all()
        return name in self.get_file_list()

    def read(self, file_name:str, mode:str="b") -> bytes|str:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        if not self.installed:
            self.install_all()
        file_name = self.get_full_file_name(file_name)
        data = self.zip_file.read(file_name)
        if mode == "r":
            return data.decode("utf-8")
        else:
            return data
    
    def get_file(self, file_name:str, mode:str="b") -> IO:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")
    
        if not self.installed:
            self.install_all()
        file_name = self.get_full_file_name(file_name)
        if mode == "b":
            return self.zip_file.open(file_name)
        else:
            temp_path = Path(FileManager.TEMP_FOLDER.joinpath(str(uuid.uuid4())))
            path_that_zipfile_puts_it_in = Path(temp_path.joinpath(file_name))
            self.zip_file.extract(file_name, temp_path)
            return open(path_that_zipfile_puts_it_in, "rt")

    def install_all(self, destination:Path|None=None) -> None:

        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")

        if destination is None: destination = self.apk_location
        if not self.apk_location.exists() and not self.installing:
            self.installing = True
            try:
                with open(destination, "wb") as f:
                    while self.current_open_connections[self.domain] >= self.connection_limit:
                        time.sleep(0.1)
                    self.current_open_connections[self.domain] += 1
                    f.write(requests.get(self.url).content)
                    self.current_open_connections[self.domain] -= 1
                self.installed = True
                self.zip_file = zipfile.ZipFile(self.apk_location)
                self.members = {member.filename: member for member in self.zip_file.filelist}
            finally:
                self.installing = False
        elif self.zip_file is None:
            self.zip_file = zipfile.ZipFile(self.apk_location)
            self.members = {member.filename: member for member in self.zip_file.filelist}
        while self.installing:
            time.sleep(0.05)
