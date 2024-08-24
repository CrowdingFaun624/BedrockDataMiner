from typing import Any

import DataMiner.BuiltIns.GrabMultipleFilesDataMiner as GrabMultipleFilesDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.File as File
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MyGrabMultipleFilesDataMiner"]

class MyGrabMultipleFilesDataMiner(GrabMultipleFilesDataMiner.GrabMultipleFilesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=FileDataMiner.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("unrecognized_suffix_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
    )

    def initialize(self, location:str, ignore_suffixes:list[str]|None=None, suffixes:list[str]|None=None, insert_pack:str|None=None, unrecognized_suffix_okay:bool=False, find_none_okay:bool=False) -> None:
        super().initialize(location, ignore_suffixes, suffixes, unrecognized_suffix_okay, find_none_okay)
        self.insert_pack = insert_pack

    def get_output(self, files: dict[str, bytes], accessor: Accessor.DirectoryAccessor, environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str, File.File|Any]:
        output:dict[str,File.File|Any] = {}
        for file_name, file_bytes in files.items():
            file_data = self.export_file(file_bytes, file_name)
            if self.insert_pack is None:
                output[file_name] = file_data
            else:
                output[file_name] = {self.insert_pack: file_data}
        return output
