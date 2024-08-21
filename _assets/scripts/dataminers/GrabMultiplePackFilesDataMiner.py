from typing import Any, Callable, Literal

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import DataMiner.DataTypes as DataTypes
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["GrabMultiplePackFilesDataMiner"]

location_function:Callable[[str,str],tuple[bool,str]] = lambda key, value: (value.endswith("/"), "location does not end in \"/\"")

class GrabMultiplePackFilesDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=location_function),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("invert", "a bool", False, bool),
    )

    @classmethod
    def manipulate_arguments(cls, arguments: dict[str, Any]) -> None:
        if "data_type" in arguments:
            arguments["data_type"] = DataTypes.DataTypes[arguments["data_type"]]

    def initialize(
        self,
        location:str,
        pack_type:Literal["resource_packs", "behavior_packs"],
        data_type:DataTypes.DataTypes=DataTypes.DataTypes.json,
        ignore_suffixes:list[str]|None=None,
        suffixes:list[str]|None=None,
        invert:bool=False, # if True, will be {pack_name: {item_name: item}} instead of {item_name: {pack_name: item}}
    ) -> None:
        self.location = location
        self.pack_type = pack_type
        self.data_type = data_type
        self.ignore_suffixes = ignore_suffixes
        self.suffixes = suffixes
        self.invert = invert

    def get_packs(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.ResourcePacks:
        return environment.dependency_data.get(self.pack_type, self)

    def get_files(self, packs:DataMinerTyping.ResourcePacks, accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[tuple[str,str],Any]:
        '''
        Returns a dict with keys as tuples of file name and pack name and values of their contents.
        '''
        files:dict[tuple[str,str],str] = {}
        for pack in packs:
            path_base = pack["path"] + self.location
            for path in accessor.get_files_in(path_base):
                if self.ignore_suffixes is not None and any(path.endswith("." + ignore_suffix) for ignore_suffix in self.ignore_suffixes):
                    continue
                if self.suffixes is None:
                    file_name = path.replace(path_base, "", 1)
                    files[file_name, pack["name"]] = DataTypes.get_data(self, path, self.data_type, accessor)
                else:
                    suffixes = [suffix for suffix in self.suffixes if path.endswith("." + suffix)]
                    if len(suffixes) == 0:
                        recognized_suffixes = self.suffixes if self.ignore_suffixes is None else (self.suffixes + self.ignore_suffixes)
                        raise Exceptions.DataMinerUnrecognizedSuffixError(self, path, recognized_suffixes)
                    suffix = "." + suffixes[0]
                    file_name = path.replace(path_base, "", 1).replace(suffix, "", 1)
                    if file_name.endswith(suffix):
                        raise Exceptions.InvalidStateError(self, "file_name still ends in \"%s\"!" % (suffix))
                    files[file_name, pack["name"]] = DataTypes.get_data(self, path, self.data_type, accessor)
        return files

    def get_output(self, files:dict[tuple[str,str],Any], environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,dict[str,Any]]:
        output:dict[str,dict[str,Any]] = {}
        for (file_name, pack_name), file_data in files.items():
            if self.invert:
                file_name, pack_name = pack_name, file_name
            if file_name not in output:
                output[file_name] = {pack_name: file_data}
            else:
                output[file_name][pack_name] = file_data
        if len(output) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return output

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        packs = environment.dependency_data.get(self.pack_type, self)
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return Sorting.sort_everything(output)
