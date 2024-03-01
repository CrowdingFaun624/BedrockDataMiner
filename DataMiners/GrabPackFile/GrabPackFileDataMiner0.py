import pyjson5 # supports comments
from typing import Any

import DataMiners.GrabPackFile.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class GrabPackFileDataMiner0(GrabPackFileDataMiner.GrabPackFileDataMiner):

    def initialize(self, **kwargs) -> None:
        if "locations" in kwargs:
            self.locations:list[str] = kwargs["locations"]
        else:
            raise ValueError("`GrabPackFileDataMiner0` was initialized without kwarg \"locations\"!")
        if "pack_type" in kwargs:
            if kwargs["pack_type"] not in ("resource_packs", "behavior_packs"):
                raise ValueError("`pack_type` must be \"resource_packs\" or \"behavior_packs\"!")
            self.pack_type:str = kwargs["pack_type"]
        else:
            raise ValueError("`GrabPackFileDataMiner0` was initialized without kwarg \"pack_type\"!")
        if "file_display_name" in kwargs:
            self.file_display_name:str|None = kwargs["file_display_name"]
        else:
            raise ValueError("`GrabPackFileDataMiner0` was initialized without kwarg \"file_display_name\"!")

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        packs = dependency_data[self.pack_type]
        pack_names = [pack["name"] for pack in packs]
        pack_files:dict[str,str] = {}
        for blocks_location in self.locations:
            pack_files.update({blocks_location % pack_name: pack_name for pack_name in pack_names})
        files_request = [(file, "t", pyjson5.load) for file in pack_files.keys()]
        files:dict[str,Any] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            if self.file_display_name is None:
                raise FileNotFoundError("No files found in \"%s\"" % self.version)
            else:
                raise FileNotFoundError("No %s files found in \"%s\"" % (self.file_display_name, self.version))

        output = {pack_files[pack_file]: loading_tips for pack_file, loading_tips in files.items()}
        return Sorting.sort_everything(output)
