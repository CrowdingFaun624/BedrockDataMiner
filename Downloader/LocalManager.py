import os
from typing import Iterable
from pathlib2 import Path

import Downloader.InstallManager as InstallManager
import Utilities.Version as Version
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller

class LocalManager(InstallManager.InstallManager):
    def prepare_for_install(self) -> None:
        if not self.version.download_method is Version.DOWNLOAD_LOCAL:
            raise ValueError("Version \"%s\" is using a LocalManager while having a \"%s\" download type!" % (self.version.name, self.version.download_method))
        if os.name == "nt": # TODO: Make this part less sucky
            windows_apps = Path("C:\Program Files\WindowsApps") 
            if self.version.download_link == "beta_local":
                search_file = "Microsoft.MinecraftWindowsBeta"
            elif self.version.download_link == "release_local":
                search_file = "Microsoft.MinecraftUWP"
            else:
                raise ValueError("Version \"%s\" does not have a valid download link for type \"local\"!" % (self.version.name))
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

    def get_file_list(self, path:Path|None) -> Iterable[str]:
        if path is None:
            strip_string = str(self.bedrock_local) + self.get_full_file_name("")
            return [path.replace(strip_string, "", 1).replace("\\", "/") for path in self.get_file_list(self.bedrock_local) if path.startswith(strip_string)]
        output:list[Path] = []
        for subpath in path.iterdir():
            subpath:Path
            if subpath.is_file():
                output.append(subpath)
            elif subpath.is_dir():
                output.extend(self.get_file_list(subpath))
        return output
    
    def file_exists(self, name:str) -> bool:
        return Path(self.bedrock_local.joinpath(self.get_full_file_name(name))).exists()

    def read(self, file_name:str, mode:str="b") -> bytes|str:

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
    
    def get_file(self, file_name:str, mode:str="b") -> FileManager.FilePromise:

        if not isinstance(file_name, str):
            raise TypeError("Parameter `file_name` is not a `str`!")
        if not isinstance(mode, str):
            raise TypeError("Parameter `mode` is not a `str`!")
        if mode not in ("t", "b"):
            raise ValueError("Parameter `mode` is not \"b\" or \"t\"!")
        
        file_name = self.get_full_file_name(file_name)
        full_path = Path(self.bedrock_local.joinpath(file_name))
        return FileManager.FilePromise(open, [full_path, "r" + mode])
    
    def all_done(self) -> None:
        pass # There is no need to do anything. All of the files are where they should be.
            