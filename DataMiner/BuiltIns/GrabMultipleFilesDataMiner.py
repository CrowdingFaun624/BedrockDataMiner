from typing import Any, Callable

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataTypes as DataTypes
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

location_function:Callable[[str,str],tuple[bool,str]] = lambda key, value: (value.endswith("/"), "location does not end in \"/\"")

class GrabMultipleFilesDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a DataType", False, TypeVerifier.EnumTypeVerifier(DataTypes.DataTypes.data_types())),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=location_function),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    def initialize(self, location:str, data_type:DataTypes.DataTypes=DataTypes.DataTypes.json, ignore_suffixes:list[str]|None=None, suffixes:list[str]|None=None, insert_pack:str|None=None) -> None:
        self.data_type = data_type
        self.location = location
        self.ignore_suffixes = ignore_suffixes
        self.suffixes = suffixes
        self.insert_pack = insert_pack

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
                    recognized_suffixes = self.suffixes if self.ignore_suffixes is None else (self.suffixes + self.ignore_suffixes)
                    raise Exceptions.DataMinerUnrecognizedSuffixError(self, path, recognized_suffixes)
                suffix = "." + suffixes[0]
                file_name = path.replace(path_base, "", 1).replace(suffix, "", 1)
                if file_name.endswith(suffix):
                    raise Exceptions.InvalidStateError(self, "file_name still ends in \"%s\"!" % (suffix))
                files[file_name] = path
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output:dict[str,dict[str,Any]] = {}
        for file_name, path in files.items():
            file_data = DataTypes.get_data(self, path, self.data_type, accessor)
            if self.insert_pack is None:
                output[file_name] = file_data
            else:
                output[file_name] = {self.insert_pack: file_data}
        return Sorting.sort_everything(output)