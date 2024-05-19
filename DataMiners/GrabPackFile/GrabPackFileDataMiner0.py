from typing import Any, Literal

import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.DataTypes as DataTypes
import DataMiners.GrabPackFile.GrabPackFileDataMiner as GrabPackFileDataMiner
import Utilities.Sorting as Sorting


class GrabPackFileDataMiner0(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "data_type": (DataMinerParameters.LiteralParameters(DataTypes.DataTypes.data_types()), False),
        "locations": (DataMinerParameters.ListParameters(str), True),
        "pack_type": (DataMinerParameters.LiteralParameters({"resource_packs", "behavior_packs"}), True),
        "file_display_name": (str, True),
    })

    def initialize(self, **kwargs) -> None:
        if "data_type" not in kwargs:
            self.data_type = DataTypes.DataTypes.json
        else:
            self.data_type = DataTypes.DataTypes[kwargs["data_type"]]
        self.locations:list[str] = kwargs["locations"]
        self.pack_type:Literal["resource_packs", "behavior_packs"] = kwargs["pack_type"]
        self.file_display_name:str|None = kwargs["file_display_name"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        packs = dependency_data[self.pack_type]
        assert packs is not None
        pack_names = [(pack["name"], pack["path"]) for pack in packs]
        pack_files:dict[str,str] = {}
        for blocks_location in self.locations:
            pack_files.update({pack_path + blocks_location: pack_name for pack_name, pack_path in pack_names})
        files_request = DataTypes.get_file_request(pack_files.keys(), self.data_type)
        accessor = self.get_accessor("client")
        files:dict[str,Any] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            if self.file_display_name is None:
                raise FileNotFoundError("No files found in \"%s\"" % self.version)
            else:
                raise FileNotFoundError("No %s files found in \"%s\"" % (self.file_display_name, self.version))

        output = {pack_files[pack_file]: data for pack_file, data in files.items()}
        return Sorting.sort_everything(output)
