from typing import Any

import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GrabMultipleFilesDataminer(FileDataminer.FileDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataminer.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=FileDataminer.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataminer.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("unrecognized_suffix_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_subdirectories", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataminer.location_item_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_files", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
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
    ) -> None:
        self.location = location
        self.ignore_suffixes = ignore_suffixes
        self.suffixes = suffixes
        self.unrecognized_suffix_okay = unrecognized_suffix_okay
        self.find_none_okay = find_none_okay
        self.ignore_subdirectories = ignore_subdirectories
        self.ignore_files:set[str] = set(ignore_files) if ignore_files is not None else set()

    def get_coverage(self, file_set:FileDataminer.FileSet, environment:DataminerEnvironment.DataminerEnvironment) -> set[str]:
        output:set[str] = set()
        for file_name in file_set.get_files_in(self.location):
            relative_name = file_name.removeprefix(self.location)
            if not (
                    (self.ignore_files is None or relative_name not in self.ignore_files)
                and (self.ignore_subdirectories is None or not any(relative_name.startswith(ignore_directory) for ignore_directory in self.ignore_subdirectories))
                and (self.ignore_suffixes is None or not any(relative_name.endswith(ignore_suffix) for ignore_suffix in self.ignore_suffixes))
            ): continue
            if self.suffixes is not None:
                if not any(file_name.endswith(suffix) for suffix in self.suffixes):
                    if self.unrecognized_suffix_okay: continue
                    else:
                        recognized_suffixes = self.suffixes if self.ignore_suffixes is None else (self.suffixes + self.ignore_suffixes)
                        raise Exceptions.DataminerUnrecognizedSuffixError(self, file_name, recognized_suffixes)
            output.add(file_name)
        if len(output) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return output

    def get_files(self, path_base:str, accessor:Accessor.DirectoryAccessor, environment:DataminerEnvironment.DataminerEnvironment) -> dict[tuple[str,str],bytes]:
        files:dict[tuple[str,str],bytes] = {}
        for file_name in accessor.get_files_in(path_base):
            should_store_file = True
            relative_name = file_name.removeprefix(path_base)
            if self.ignore_files is not None and relative_name in self.ignore_files:
                continue
            if self.ignore_suffixes is not None and any(relative_name.endswith(ignore_suffix) for ignore_suffix in self.ignore_suffixes):
                continue
            if self.ignore_subdirectories is not None and any(relative_name.startswith(ignore_directory) for ignore_directory in self.ignore_subdirectories):
                continue
            if self.suffixes is not None:
                for suffix in self.suffixes:
                    if file_name.endswith(suffix):
                        # relative_name = relative_name.removesuffix(suffix)
                        break
                else:
                    # this file's name does not end in any recognized suffix
                    if self.unrecognized_suffix_okay:
                        should_store_file = False
                        continue
                    else:
                        recognized_suffixes = self.suffixes if self.ignore_suffixes is None else (self.suffixes + self.ignore_suffixes)
                        raise Exceptions.DataminerUnrecognizedSuffixError(self, file_name, recognized_suffixes)

            if should_store_file:
                files[relative_name, file_name] = accessor.read(file_name)

        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str],bytes], accessor:Accessor.DirectoryAccessor, environment:DataminerEnvironment.DataminerEnvironment) -> dict[str,File.File|Any]:
        return {relative_name: self.export_file(file_bytes, file_name) for (relative_name, file_name), file_bytes in files.items()}

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        files = self.get_files(self.location, accessor, environment)
        output = self.get_output(files, accessor, environment)
        return output
