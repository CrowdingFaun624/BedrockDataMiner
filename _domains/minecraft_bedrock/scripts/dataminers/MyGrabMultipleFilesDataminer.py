from typing import Any

import Dataminer.BuiltIns.GrabMultipleFilesDataminer as GrabMultipleFilesDataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Downloader.DirectoryAccessor as DirectoryAccessor
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["MyGrabMultipleFilesDataminer"]

class MyGrabMultipleFilesDataminer(GrabMultipleFilesDataminer.GrabMultipleFilesDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", False, TypeVerifier.ListTypeVerifier(str, list, item_function=FileDataminer.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("location", True, str, function=FileDataminer.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", False, TypeVerifier.ListTypeVerifier(str, list, item_function=FileDataminer.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("unrecognized_suffix_okay", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_subdirectories", False, TypeVerifier.ListTypeVerifier(str, list, item_function=FileDataminer.location_item_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_files", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("reverse", False, bool),
    )

    def initialize(
        self,
        location:str,
        ignore_suffixes:list[str]|None=None,
        suffixes:list[str]|None=None,
        unrecognized_suffix_okay:bool=False,
        find_none_okay:bool=False,
        ignore_subdirectories:list[str]|None=None,
        ignore_files:list[str]|None=None,
        insert_pack:str|None=None,
        reverse:bool=False,
    ) -> None:
        super().initialize(location, ignore_suffixes, suffixes, unrecognized_suffix_okay, find_none_okay, ignore_subdirectories, ignore_files)
        self.insert_pack = insert_pack
        self.reverse = reverse

    def get_output(self, files: dict[str, bytes], accessor: DirectoryAccessor.DirectoryAccessor, environment: DataminerEnvironment.DataminerEnvironment) -> dict[str, File.File|Any]:
        output:dict[str,Any] = {}
        for (relative_name, file_name), file_bytes in files.items():
            file_data = self.export_file(file_bytes, file_name)
            if self.insert_pack is None:
                output[relative_name] = file_data
            elif self.reverse:
                if self.insert_pack not in output:
                    output[self.insert_pack] = {}
                output[self.insert_pack][relative_name] = file_data
            else:
                output[relative_name] = {self.insert_pack: file_data}
        return output
