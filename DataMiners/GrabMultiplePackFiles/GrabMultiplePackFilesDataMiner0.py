import pyjson5 # supports comments
from typing import Any

import DataMiners.GrabMultiplePackFiles.GrabMultiplePackFilesDataMiner as GrabMultiplePackFilesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class GrabMultiplePackFilesDataMiner0(GrabMultiplePackFilesDataMiner.GrabMultiplePackFilesDataMiner):

    def initialize(self, **kwargs) -> None:
        if "location" in kwargs:
            self.location:str = kwargs["location"]
        else:
            raise ValueError("`GrabMultiplePackFilesDataMiner0` was initialized without kwarg \"location\"!")
        if "pack_type" in kwargs:
            if kwargs["pack_type"] not in ("resource_packs", "behavior_packs"):
                raise ValueError("`pack_type` must be \"resource_packs\" or \"behavior_packs\"!")
            self.pack_type:str = kwargs["pack_type"]
        else:
            raise ValueError("`GrabMultiplePackFilesDataMiner0` was initialized without kwarg \"pack_type\"!")
        if "suffixes" in kwargs:
            self.suffixes:list[str]|None = kwargs["suffixes"]
        else:
            raise ValueError("`GrabMultiplePackFilesDataMiner0` was initialized without kwarg \"suffixes\"!")
        if "file_display_name" in kwargs:
            self.file_display_name:str|None = kwargs["file_display_name"]
        else:
            raise ValueError("`GrabMultiplePackFilesDataMiner0` was initialized without kwarg \"file_display_name\"!")

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        packs = dependency_data[self.pack_type]
        files:dict[tuple[str,str],str] = {}
        for pack in packs:
            path_base = self.location % pack["name"]
            for path in self.get_files_in(path_base):
                if self.suffixes is None:
                    file_name = path.replace(path_base, "", 1)
                    files[file_name, pack["name"]] = path
                else:
                    suffixes = [suffix for suffix in self.suffixes if path.endswith("." + suffix)]
                    if len(suffixes) == 0:
                        raise ValueError("Unrecognized suffix on path \"%s\"!" % path)
                    suffix = "." + suffixes[0]
                    file_name = path.replace(path_base, "", 1).replace(suffix, "", 1)
                    assert not file_name.endswith(suffix)
                    files[file_name, pack["name"]] = path
        if len(files) == 0:
            if self.file_display_name is None:
                raise FileNotFoundError("No files found in \"%s\"" % self.version)
            else:
                raise FileNotFoundError("No %s files found in \"%s\"" % (self.file_display_name, self.version))

        output:dict[str,dict[str,Any]] = {}
        for (file_name, pack_name), path in files.items():
            file_data = pyjson5.loads(self.read_file(path))
            if file_name not in output:
                output[file_name] = {pack_name: file_data}
            else:
                output[file_name][pack_name] = file_data
        return Sorting.sort_everything(output)
