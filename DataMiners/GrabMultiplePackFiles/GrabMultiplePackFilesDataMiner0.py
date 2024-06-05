from typing import Any, Callable, Literal

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.DataTypes as DataTypes
import DataMiners.GrabMultiplePackFiles.GrabMultiplePackFilesDataMiner as GrabMultiplePackFilesDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

location_function:Callable[[str,str],tuple[bool,str]] = lambda key, value: (value.endswith("/"), "location does not end in \"/\"")

class GrabMultiplePackFilesDataMiner0(GrabMultiplePackFilesDataMiner.GrabMultiplePackFilesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=location_function),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def initialize(self, **kwargs) -> None:
        self.data_type = DataTypes.DataTypes[kwargs.get("data_type", "json")]
        self.ignore_suffixes:list[str]|None = kwargs.get("ignore_suffixes", None)
        self.location:str = kwargs["location"]
        self.pack_type:Literal["resource_packs", "behavior_packs"] = kwargs["pack_type"]
        self.suffixes:list[str]|None = kwargs.get("suffixes", None)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        packs:DataMinerTyping.ResourcePacks|DataMinerTyping.BehaviorPacks = environment.dependency_data.get(self.pack_type, self)
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
                        recognized_suffixes = self.suffixes if self.ignore_suffixes is None else (self.suffixes + self.ignore_suffixes)
                        raise Exceptions.DataMinerUnrecognizedSuffixError(self, path, recognized_suffixes)
                    suffix = "." + suffixes[0]
                    file_name = path.replace(path_base, "", 1).replace(suffix, "", 1)
                    if file_name.endswith(suffix):
                        raise Exceptions.InvalidStateError(self, "file_name still ends in \"%s\"!" % (suffix))
                    files[file_name, pack["name"]] = path

        output:dict[str,dict[str,Any]] = {}
        for (file_name, pack_name), path in files.items():
            file_data = DataTypes.get_data(self, path, self.data_type, accessor)
            if file_name not in output:
                output[file_name] = {pack_name: file_data}
            else:
                output[file_name][pack_name] = file_data

        if len(output) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        return Sorting.sort_everything(output)
