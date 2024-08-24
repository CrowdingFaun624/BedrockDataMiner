from typing import Any

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabMultipleFilesDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=FileDataMiner.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("unrecognized_suffix_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_subdirectories", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.location_item_function)),
    )

    def initialize(self, location:str, ignore_suffixes:list[str]|None=None, suffixes:list[str]|None=None, unrecognized_suffix_okay:bool=False, find_none_okay:bool=False, ignore_subdirectories:list[str]|None=None) -> None:
        self.location = location
        self.ignore_suffixes = ignore_suffixes
        self.suffixes = suffixes
        self.unrecognized_suffix_okay = unrecognized_suffix_okay
        self.find_none_okay = find_none_okay
        self.ignore_subdirectories = ignore_subdirectories

    def get_coverage(self, file_set: set[str], environment:DataMinerEnvironment.DataMinerEnvironment) -> set[str]:
        ignore_directories = [self.location + subdirectory for subdirectory in self.ignore_subdirectories] if self.ignore_subdirectories is not None else None
        return {
            file_name
            for file_name in file_set
            if file_name.startswith(self.location)
            if ignore_directories is None or not any(file_name.startswith(ignore_directory) for ignore_directory in ignore_directories)
            if self.ignore_suffixes is None or not any(file_name.endswith(ignore_suffix) for ignore_suffix in self.ignore_suffixes)
            if self.suffixes is None or any(file_name.endswith(suffix) for suffix in self.suffixes)
        }

    def get_files(self, path_base:str, accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[tuple[str,str],bytes]:
        files:dict[tuple[str,str],bytes] = {}
        ignore_directories = [self.location + subdirectory for subdirectory in self.ignore_subdirectories] if self.ignore_subdirectories is not None else None
        for file_name in accessor.get_files_in(path_base):
            should_store_file = True
            if self.ignore_suffixes is not None and any(file_name.endswith(ignore_suffix) for ignore_suffix in self.ignore_suffixes):
                continue
            if ignore_directories is not None and any(file_name.startswith(ignore_directory) for ignore_directory in ignore_directories):
                continue
            relative_name = file_name.replace(path_base, "", 1)
            if self.suffixes is not None:
                for suffix in self.suffixes:
                    if file_name.endswith(suffix):
                        relative_name = relative_name.removesuffix(suffix)
                        break
                else:
                    # this file's name does not end in any recognized suffix
                    if self.unrecognized_suffix_okay:
                        should_store_file = False
                        continue
                    else:
                        recognized_suffixes = self.suffixes if self.ignore_suffixes is None else (self.suffixes + self.ignore_suffixes)
                        raise Exceptions.DataMinerUnrecognizedSuffixError(self, file_name, recognized_suffixes)

            if should_store_file:
                files[relative_name, file_name] = accessor.read(file_name, "b")

        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataMinerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str],bytes], accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,File.File|Any]:
        return {relative_name: self.export_file(file_bytes, file_name) for (relative_name, file_name), file_bytes in files.items()}

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        files = self.get_files(self.location, accessor, environment)
        output = self.get_output(files, accessor, environment)
        return Sorting.sort_everything(output)
