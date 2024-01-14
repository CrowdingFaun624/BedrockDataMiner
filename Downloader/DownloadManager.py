from typing import Iterable, TYPE_CHECKING
from pathlib2 import Path
import requests
import shutil
import threading
import time
from urllib.parse import urlparse
import zipfile

import Downloader.InstallManager as InstallManager
import Utilities.FileManager as FileManager
import Utilities.VersionTags as VersionTags
from Utilities.FunctionCaller import FunctionCaller

if TYPE_CHECKING:
    import Utilities.Version as Version

CONNECTION_LIMITS:dict[str,int] = {}
CONNECTION_LIMITS_DEFAULT = 1

class DownloadManager(InstallManager.InstallManager):
    current_open_connections:dict[str,list[requests.Request]] = {}

    def prepare_for_install(self) -> None:
        self.apk_location = Path(str(self.location) + ".zip")
        self.url = None
        self.installed = self.apk_location.exists()

        if self.installed: # If it's already installed, do stuff that's only done in self.install.
            self.zip_file = zipfile.ZipFile(self.apk_location)
            self.members = {member.filename: member for member in self.zip_file.filelist}
        else:
            self.zip_file = None
            self.members = None

        self.file_list = None
        self.installation_lock = threading.Lock()
        self.get_file_list_lock = threading.Lock()

        self.url = self.version.download_link
        self.domain = urlparse(self.url).netloc
        if self.domain not in self.current_open_connections:
            self.current_open_connections[self.domain] = 0
        self.connection_limit = CONNECTION_LIMITS[self.domain] if self.domain in CONNECTION_LIMITS else CONNECTION_LIMITS_DEFAULT
        self.set_file_prepension()

    def set_file_prepension(self) -> None:
        tags = self.version.tags
        if VersionTags.IPA in tags:
            prepend = "Payload/minecraftpe.app/data/"
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
        if self.file_list is None:
            with self.get_file_list_lock:
                if self.file_list is not None:
                    return self.file_list # If it started waiting and then it's complete when it's done waiting.
                strip_string = self.get_full_file_name("")
                self.file_list = [file.filename.replace(strip_string, "", 1) for file in self.zip_file.filelist if file.filename.startswith(strip_string)]
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
        if mode == "t":
            return data.decode("utf-8")
        else:
            return data
    
    def get_file(self, file_name:str, mode:str="b") -> FileManager.FilePromise:

        def clear_temp_file(temp_path:Path, path_that_zipfile_puts_it_in:Path) -> None:
            path_that_zipfile_puts_it_in.unlink()
            folders_to_remove:list[Path] = [temp_path] # with `temp_path` so that it removes the base, temporary path name
            current_path = temp_path
            while True:
                children = list(current_path.iterdir())
                if len(children) == 0:
                    break
                assert len(children) == 1
                folders_to_remove.extend(children)
                current_path = children[0]
            for folder_to_remove in reversed(folders_to_remove):
                folder_to_remove.rmdir()

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
            return FileManager.FilePromise(FunctionCaller(self.zip_file.open, [file_name]), file_name.split("/")[-1], mode)
        else:
            temp_path = FileManager.get_temp_file_path()
            path_that_zipfile_puts_it_in = Path(temp_path.joinpath(file_name))
            self.zip_file.extract(file_name, temp_path)
            return FileManager.FilePromise(FunctionCaller(open, [path_that_zipfile_puts_it_in, "rt"]), file_name.split("/")[-1], mode, FunctionCaller(clear_temp_file, [temp_path, path_that_zipfile_puts_it_in]))

    def install_all(self, destination:Path|None=None) -> None:

        if destination is not None and not isinstance(destination, Path):
            raise TypeError("Parameter `destination` is not a `Path`!")

        self.installation_lock.acquire()
        if destination is None: destination = self.apk_location
        if not self.installed:
            with open(destination, "wb") as f:
                while self.current_open_connections[self.domain] >= self.connection_limit:
                    time.sleep(0.1)
                self.current_open_connections[self.domain] += 1
                f.write(requests.get(self.url).content)
                self.current_open_connections[self.domain] -= 1
            self.installed = True
            self.zip_file = zipfile.ZipFile(self.apk_location)
            self.members = {member.filename: member for member in self.zip_file.filelist}
        self.installation_lock.release()
    
    def all_done(self) -> None:
        self.installation_lock.acquire() # So it doesn't do anything under my nose
        self.installed = False
        self.zip_file = None
        self.members = None
        if self.apk_location.exists():
            self.apk_location.unlink()
        assert self.location.name != self.version.name # self.location refers to the `client` subdirectory of the version folder.
        if self.location.exists():
            shutil.rmtree(self.location)
        self.installation_lock.release()
