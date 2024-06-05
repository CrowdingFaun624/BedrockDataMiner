import shutil
import zipfile
from typing import Literal, TypedDict

import requests
from pathlib2 import Path

import Downloader.DownloadLog as DownloadLog
import Downloader.Manager as Manager
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Version.VersionTags as VersionTags
from Utilities.FunctionCaller import FunctionCaller, WaitValue


class DownloadManagerTypedDict(TypedDict):
    url: str

class DownloadManager(Manager.Manager):

    def prepare_for_install(self, version_tags:VersionTags.VersionTags, file_type_arguments:DownloadManagerTypedDict) -> None:
        self.apk_location = self.location
        self.installed = WaitValue(self.apk_location.exists)

        self.has_zip_file_opened = False

        self.file_list:list[str]|None = None
        self.file_set:set[str]|None = None

        self.url = file_type_arguments["url"]

    def open_zip_file(self) -> None:
        '''Opens the zip file if it hasn't already.'''
        if not self.has_zip_file_opened:
            if not self.installed.get():
                self.install_all()
            self.zip_file = zipfile.ZipFile(self.apk_location)
            self.members = {member.filename: member for member in self.zip_file.filelist}
            self.has_zip_file_opened = True

    def get_files_in(self, parent: str) -> list[str]:
        return [file for file in self.get_file_list() if file.startswith(parent)]

    def get_file_list(self) -> list[str]:
        if not self.installed.get():
            self.install_all()
        self.open_zip_file()
        if self.file_list is None:
            if self.file_list is not None:
                return self.file_list # If it started waiting and then it's complete when it's done waiting.
            if self.zip_file is None:
                raise Exceptions.AttributeNoneError("zip_file", self)
            self.file_list = [file.filename for file in self.zip_file.filelist]
            self.file_set = set(self.file_list)
        return self.file_list

    def get_file_set(self) -> set[str]:
        if self.file_set is None:
            self.get_file_list()
        if self.file_set is None:
            raise Exceptions.AttributeNoneError("file_set", self)
        return self.file_set

    def file_exists(self, file_name:str) -> bool:
        if not self.installed.get():
            self.install_all()
        return file_name in self.get_file_set()

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        if not self.installed.get():
            self.install_all()
        self.open_zip_file()
        if self.zip_file is None:
            raise Exceptions.AttributeNoneError("zip_file", self)
        data = self.zip_file.read(file_name)
        if mode == "t":
            return data.decode("utf-8")
        else:
            return data

    def get_file(self, file_name:str, mode:Literal["b","t"]="b") -> FileManager.FilePromise:

        def clear_temp_file(temp_path:Path, path_that_zipfile_puts_it_in:Path) -> None:
            path_that_zipfile_puts_it_in.unlink()
            directories_to_remove:list[Path] = [temp_path] # with `temp_path` so that it removes the base, temporary path name
            current_path = temp_path
            while True:
                children = list(current_path.iterdir())
                if len(children) == 0:
                    break
                if len(children) != 1:
                    raise Exceptions.InvalidStateError(self, children, "too many children!")
                directories_to_remove.extend(children)
                current_path = children[0]
            for directory_to_remove in reversed(directories_to_remove):
                directory_to_remove.rmdir()

        if not self.installed.get():
            self.install_all()
        self.open_zip_file()
        if self.zip_file is None:
            raise Exceptions.AttributeNoneError("zip_file", self)
        if mode == "b":
            return FileManager.FilePromise(FunctionCaller(self.zip_file.open, [file_name]), file_name.split("/")[-1], mode)
        else:
            temp_path = FileManager.get_temp_file_path()
            path_that_zipfile_puts_it_in = temp_path.joinpath(file_name)
            self.zip_file.extract(file_name, temp_path)
            return FileManager.FilePromise(FunctionCaller(open, [path_that_zipfile_puts_it_in, "rt"]), file_name.split("/")[-1], mode, FunctionCaller(clear_temp_file, [temp_path, path_that_zipfile_puts_it_in]))

    def install_all(self, destination:Path|None=None) -> None:
        if destination is None: destination = self.apk_location
        if not self.installed.get():
            response_supposed_length = None
            response_length = 0
            tries = 0
            while response_supposed_length is None or response_supposed_length != response_length:
                with open(destination, "wb") as f:
                    with requests.get(self.url) as response:
                        response_length = len(response.content)
                        response_supposed_length = int(response.headers.get("Content-Length", "0"))
                        DownloadLog.log(self.version, response, response_length)
                        f.write(response.content)
                tries += 1
                if tries >= 5:
                    raise Exceptions.DownloadManagerFailError(self, self.url)
            self.installed.set(True)
            self.open_zip_file()

    def all_done(self) -> None:
        self.installed.set(False)
        self.zip_file = None
        self.members = None
        self.has_zip_file_opened = False
        if self.apk_location.exists():
            self.apk_location.unlink()
        if self.location.name == self.version.name: # self.location refers to the `client` subdirectory of the version directory.
            raise Exceptions.InvalidStateError(self.location.name, self.version.name, "These should not be the same!")
        if self.location.exists():
            shutil.rmtree(self.location)
