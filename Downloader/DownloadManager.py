import shutil
import zipfile
from typing import Iterable, Literal, TypedDict

import requests
from pathlib2 import Path

import Downloader.DownloadLog as DownloadLog
import Downloader.InstallManager as InstallManager
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.VersionTags as VersionTags
from Utilities.FunctionCaller import FunctionCaller, WaitValue


class DownloadManagerTypedDict(TypedDict):
    url: str

class DownloadManager(InstallManager.InstallManager):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("url", "a str", True, str),
    )

    def prepare_for_install(self, version_tags:VersionTags.VersionTags, file_type_arguments:DownloadManagerTypedDict) -> None:
        self.apk_location = self.location
        self.installed = WaitValue(self.apk_location.exists)

        self.has_zip_file_opened = False

        self.file_list:list[str]|None = None
        self.file_set:set[str]|None = None

        self.url = file_type_arguments["url"]
        self.set_file_prepension(version_tags)

    def open_zip_file(self) -> None:
        '''Opens the zip file if it hasn't already.'''
        if not self.has_zip_file_opened:
            if not self.installed.get():
                self.install_all()
            self.zip_file = zipfile.ZipFile(self.apk_location)
            self.members = {member.filename: member for member in self.zip_file.filelist}
            self.has_zip_file_opened = True

    def set_file_prepension(self, version_tags:VersionTags.VersionTags) -> None:
        tags = self.version.tags
        if version_tags["ipa"] in tags:
            prepend = "Payload/minecraftpe.app/data/"
        else:
            if version_tags["double_assets"] in tags:
                prepend = "assets/assets/"
            else:
                prepend = "assets/"
        self.file_prepension = prepend

    def get_full_file_name(self, asset_name:str) -> str:
        return self.file_prepension + asset_name

    def get_files_in(self, parent: str) -> Iterable[str]:
        return [file for file in self.get_file_list() if file.startswith(parent)]

    def get_file_list(self) -> list[str]:
        if not self.installed.get():
            self.install_all()
        self.open_zip_file()
        if self.file_list is None:
            if self.file_list is not None:
                return self.file_list # If it started waiting and then it's complete when it's done waiting.
            strip_string = self.get_full_file_name("")
            assert self.zip_file is not None
            self.file_list = [file.filename.replace(strip_string, "", 1) for file in self.zip_file.filelist if file.filename.startswith(strip_string) and not file.filename.endswith("/")]
            self.file_set = set(self.file_list)
        return self.file_list

    def get_file_set(self) -> set[str]:
        if self.file_set is None:
            self.get_file_list()
        assert self.file_set is not None
        return self.file_set

    def get_full_file_list(self) -> list[str]:
        if not self.installed.get():
            self.install_all()
        self.open_zip_file()
        assert self.zip_file is not None
        return [file.filename for file in self.zip_file.filelist]

    def file_exists(self, name:str) -> bool:
        if not self.installed.get():
            self.install_all()
        return name in self.get_file_set()

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        if not self.installed.get():
            self.install_all()
        file_name = self.get_full_file_name(file_name)
        self.open_zip_file()
        assert self.zip_file is not None
        data = self.zip_file.read(file_name)
        if mode == "t":
            return data.decode("utf-8")
        else:
            return data

    def get_file(self, file_name:str, mode:Literal["b","t"]="b") -> FileManager.FilePromise:

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

        if not self.installed.get():
            self.install_all()
        file_name = self.get_full_file_name(file_name)
        self.open_zip_file()
        assert self.zip_file is not None
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

        if destination is None: destination = self.apk_location
        if not self.installed.get():
            response_supposed_length = None
            response_length = 0
            tries = 0
            while response_supposed_length is None or response_supposed_length != response_length:
                with open(destination, "wb") as f:
                    with requests.get(self.url) as response:
                        response_length = len(response.content)
                        response_supposed_length = int(response.headers["Content-Length"])
                        DownloadLog.log(self.version, response, response_length)
                        f.write(response.content)
                tries += 1
                if tries >= 5:
                    raise RuntimeError("Failed to correctly download file!")
            self.installed.set(True)
            self.open_zip_file()

    def all_done(self) -> None:
        self.installed.set(False)
        self.zip_file = None
        self.members = None
        self.has_zip_file_opened = False
        if self.apk_location.exists():
            self.apk_location.unlink()
        assert self.location.name != self.version.name # self.location refers to the `client` subdirectory of the version folder.
        if self.location.exists():
            shutil.rmtree(self.location)
