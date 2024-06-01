import os
from typing import Literal, TypedDict

from pathlib2 import Path

import Downloader.Manager as Manager
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.VersionTags as VersionTags
from Utilities.FunctionCaller import FunctionCaller


class LocalManagerTypedDict(TypedDict):
    is_preview: bool

class LocalManager(Manager.Manager):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("is_preview", "a bool", True, bool),
    )

    def prepare_for_install(self, version_tags:VersionTags.VersionTags, file_type_arguments:LocalManagerTypedDict) -> None:
        self.file_list:list[str]|None = None
        if os.name == "nt": # TODO: Make this part less sucky
            windows_apps = Path("C:\\Program Files\\WindowsApps")
            if file_type_arguments["is_preview"]:
                search_file = "Microsoft.MinecraftWindowsBeta"
            else:
                search_file = "Microsoft.MinecraftUWP"
            for window_file in windows_apps.iterdir():
                if window_file.name.startswith(search_file):
                    self.bedrock_local = window_file
                    break
            else:
                raise FileNotFoundError("No \"%s\" directory found in \"%s\"! Is it installed correctly?" % (search_file, windows_apps))
        else:
            raise NotImplementedError("OS type \"%s\" is not implemented!" % (os.name))

    def install_all(self, destination:Path|None=None) -> None:
        pass # There is no need to do anything. All of the files are already there.

    def get_files_in(self, parent:str) -> list[str]:
        return [file for file in self.get_file_list() if file.startswith(parent)]

    def get_file_list(self, path:Path|None=None) -> list[str]:
        if path is None:
            if self.file_list is None:
                strip_string = self.bedrock_local.as_posix() + "/"
                output:list[str] = []
                for file_path in self.get_file_list(self.bedrock_local):
                    output.append(file_path.replace(strip_string, "", 1))
                self.file_list = output
            return self.file_list
        else:
            output:list[str] = []
            for subpath in path.iterdir():
                if subpath.is_file():
                    output.append(subpath.as_posix())
                elif subpath.is_dir():
                    output.extend(self.get_file_list(subpath))
            return output

    def file_exists(self, name:str) -> bool:
        return self.bedrock_local.joinpath(name).exists()

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        full_path = self.bedrock_local.joinpath(file_name)
        with open(full_path, "r" + mode) as f:
            return f.read()

    def get_file(self, file_name:str, mode:Literal["b","t"]="b") -> FileManager.FilePromise:
        full_path = self.bedrock_local.joinpath(file_name)
        return FileManager.FilePromise(FunctionCaller(open, [full_path, "r" + mode]), file_name.split("/")[-1], mode)

    def all_done(self) -> None:
        pass # There is no need to do anything. All of the files are where they should be.
