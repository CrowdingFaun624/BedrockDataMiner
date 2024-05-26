from typing import Any, Literal

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataTypes as DataTypes
import DataMiners.GrabMultiplePackFiles.GrabMultiplePackFilesDataMiner as GrabMultiplePackFilesDataMiner
import Utilities.Sorting as Sorting


class GrabMultiplePackFilesDataMiner0(GrabMultiplePackFilesDataMiner.GrabMultiplePackFilesDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "data_type": (DataMinerParameters.LiteralParameters(DataTypes.DataTypes.data_types()), False),
        "ignore_suffixes": (DataMinerParameters.ListParameters(str), False),
        "location": (str, True),
        "pack_type": (DataMinerParameters.LiteralParameters({"resource_packs", "behavior_packs"}), True),
        "suffixes": (DataMinerParameters.ListParameters(str), False),
        "file_display_name": ((str, type(None)), True),
    })

    def initialize(self, **kwargs) -> None:
        if "data_type" not in kwargs:
            self.data_type = DataTypes.DataTypes.json
        else:
            self.data_type = DataTypes.DataTypes[kwargs["data_type"]]
        if "ignore_suffixes" in kwargs:
            self.ignore_suffixes:list[str]|None = kwargs["ignore_suffixes"]
        else:
            self.ignore_suffixes = None
        self.location:str = kwargs["location"]
        if not self.location.endswith("/"):
            raise ValueError("\"location\" \"%s\" does not end in \"/\"!" % (self.location))
        self.pack_type:Literal["resource_packs", "behavior_packs"] = kwargs["pack_type"]
        if "suffixes" in kwargs:
            self.suffixes:list[str]|None = kwargs["suffixes"]
        else:
            self.suffixes = None
        self.file_display_name:str|None = kwargs["file_display_name"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        packs = environment.dependency_data[self.pack_type]
        assert packs is not None
        files:dict[tuple[str,str],str] = {}
        accessor = self.get_accessor("client")
        for pack in packs:
            path_base = pack["path"] + self.location
            for path in accessor.get_files_in(path_base):
                if self.ignore_suffixes is not None and any(path.endswith("." + ignore_suffix) for ignore_suffix in self.ignore_suffixes):
                    continue
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

        output:dict[str,dict[str,Any]] = {}
        for (file_name, pack_name), path in files.items():
            file_data = DataTypes.get_data(self, path, self.data_type, accessor)
            if file_name not in output:
                output[file_name] = {pack_name: file_data}
            else:
                output[file_name][pack_name] = file_data

        if len(output) == 0:
            if self.file_display_name is None:
                raise FileNotFoundError("No files found in \"%s\"" % self.version)
            else:
                raise FileNotFoundError("No %s files found in \"%s\"" % (self.file_display_name, self.version))

        return Sorting.sort_everything(output)
