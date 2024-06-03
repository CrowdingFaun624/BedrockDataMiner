from typing import Any, Callable

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataTypes as DataTypes
import DataMiners.GrabMultipleFiles.GrabMultipleFilesDataMiner as GrabMultipleFilesDataMiner
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

location_function:Callable[[str,str],tuple[bool,str]] = lambda key, value: (value.endswith("/"), "location does not end in \"/\"")

class GrabMultipleFilesDataMiner0(GrabMultipleFilesDataMiner.GrabMultipleFilesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=location_function),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    def initialize(self, **kwargs) -> None:
        self.data_type = DataTypes.DataTypes[kwargs.get("data_type", "json")]
        self.ignore_suffixes:list[str]|None = kwargs.get("ignore_suffixes", None)
        self.location:str = kwargs["location"]
        self.suffixes:list[str]|None = kwargs.get("suffixes", None)
        self.insert_pack:str|None = kwargs.get("insert_pack", None)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        files:dict[str,str] = {}
        path_base = self.location
        accessor = self.get_accessor("client")
        for path in accessor.get_files_in(path_base):
            if self.ignore_suffixes is not None and any(path.endswith("." + ignore_suffix) for ignore_suffix in self.ignore_suffixes):
                continue
            if self.suffixes is None:
                file_name = path.replace(path_base, "", 1)
                files[file_name] = path
            else:
                suffixes = [suffix for suffix in self.suffixes if path.endswith("." + suffix)]
                if len(suffixes) == 0:
                    raise ValueError("Unrecognized suffix on path \"%s\"!" % path)
                suffix = "." + suffixes[0]
                file_name = path.replace(path_base, "", 1).replace(suffix, "", 1)
                assert not file_name.endswith(suffix)
                files[file_name] = path
        if len(files) == 0:
            raise FileNotFoundError("No files found in \"%s\"" % self.version)

        output:dict[str,dict[str,Any]] = {}
        for file_name, path in files.items():
            file_data = DataTypes.get_data(self, path, self.data_type, accessor)
            if self.insert_pack is None:
                output[file_name] = file_data
            else:
                output[file_name] = {self.insert_pack: file_data}
        return Sorting.sort_everything(output)
