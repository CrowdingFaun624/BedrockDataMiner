import os
from typing import Iterable, Literal, TypedDict

from pathlib2 import Path

import Downloader.InstallManager as InstallManager
import Utilities.FileManager as FileManager
import Version.VersionTags as VersionTags
from Utilities.FunctionCaller import FunctionCaller
import Utilities.TypeVerifier as TypeVerifier


class LocalManagerTypedDict(TypedDict):
    is_preview: bool

class LocalManager(InstallManager.InstallManager):

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
                window_file:Path
                if window_file.name.startswith(search_file):
                    self.bedrock_local = window_file
                    break
            else:
                raise FileNotFoundError("No \"%s\" directory found in \"%s\"! Is it installed correctly?" % (search_file, windows_apps))
        else:
            raise NotImplementedError("OS type \"%s\" is not implemented!" % (os.name))

    def get_full_file_name(self, asset_name:str) -> str:
        return "data/" + asset_name

    def install_all(self, destination:Path|None=None) -> None:
        pass # There is no need to do anything. All of the files are already there.

    def install(self, file_name:str, destination:Path|None=None) -> Path:
        # There is no need to do anything else. All of the files are already there.
        return Path(self.bedrock_local.joinpath(self.get_full_file_name(file_name)))

    def get_files_in(self, parent:str) -> Iterable[str]:
        return [file for file in self.get_file_list() if file.startswith(parent)]

    def get_file_list(self, path:Path|None=None) -> Iterable[str]:
        if path is None:
            if self.file_list is None:
                strip_string1 = self.bedrock_local.as_posix() + "/"
                strip_string2 = self.get_full_file_name("")
                output:list[str] = []
                for file_path in self.get_file_list(self.bedrock_local):
                    stripped_path = file_path.replace(strip_string1, "", 1)
                    if stripped_path.startswith(strip_string2):
                        output.append(stripped_path.replace(strip_string2, ""))
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

    def get_full_file_list(self, path:Path|None=None) -> list[str]:
        if path is None:
            if self.file_list is None:
                strip_string1 = self.bedrock_local.as_posix() + "/"
                self.file_list = [file_path.replace(strip_string1, "", 1) for file_path in self.get_file_list(self.bedrock_local)]
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
        return Path(self.bedrock_local.joinpath(self.get_full_file_name(name))).exists()

    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        file_name = self.get_full_file_name(file_name)
        full_path = Path(self.bedrock_local.joinpath(file_name))
        with open(full_path, "r" + mode) as f:
            return f.read()

    def get_file(self, file_name:str, mode:Literal["b","t"]="b", is_in_assets:bool=True) -> FileManager.FilePromise:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")

        if is_in_assets:
            file_name = self.get_full_file_name(file_name)
        full_path = Path(self.bedrock_local.joinpath(file_name))
        return FileManager.FilePromise(FunctionCaller(open, [full_path, "r" + mode]), file_name.split("/")[-1], mode)

    def all_done(self) -> None:
        pass # There is no need to do anything. All of the files are where they should be.
