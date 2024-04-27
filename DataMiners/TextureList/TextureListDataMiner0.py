import pyjson5 # supports comments
from typing import Any

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.TextureList.TextureListDataMiner as TextureListDataMiner
import Utilities.Sorting as Sorting

class TextureListDataMiner0(TextureListDataMiner.TextureListDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "locations": (DataMinerParameters.ListParameters(str), True),
    })

    def initialize(self, **kwargs) -> None:
        self.locations:list[str] = kwargs["locations"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> dict[str,list[str]]:
        packs = dependency_data["resource_packs"]
        assert packs is not None
        pack_names = [(pack["name"], pack["path"]) for pack in packs]
        pack_files:dict[str,str] = {}
        for blocks_location in self.locations:
            pack_files.update({pack_path + blocks_location: pack_name for pack_name, pack_path in pack_names})
        files_request = [(file, "t", None) for file in pack_files.keys()]
        files:dict[str,str] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No texture_list files found in \"%s\"" % (self.version))

        output = {pack_files[pack_file]: texture_list.splitlines() for pack_file, texture_list in files.items()}
        return Sorting.sort_everything(output)
