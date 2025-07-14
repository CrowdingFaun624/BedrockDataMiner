from itertools import product
from typing import Any, Sequence

import Dataminer.FileDataminer as FileDataminer
import Utilities.Exceptions as Exceptions
from _domains.minecraft_java.scripts.dataminers.PacksDataminer import PackTypedDict
from Component.ComponentFunctions import component_function
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.File import File
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


@component_function()
class GrabMultiplePackFilesDataminer(FileDataminer.FileDataminer):

    __slots__ = (
        "find_none_okay",
        "ignore_any_directories",
        "ignore_files",
        "ignore_subdirectories",
        "ignore_suffixes",
        "location",
        "pack_or_namespace",
        "pack_type",
        "suffixes",
        "unrecognized_suffix_okay",
    )

    parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("ignore_suffixes", False, ListTypeVerifier(str, list, item_function=FileDataminer.suffix_function)),
        TypedDictKeyTypeVerifier("location", True, UnionTypeVerifier(str, ListTypeVerifier(str, list, item_function=FileDataminer.location_item_function)), function=lambda key, value: FileDataminer.location_value_function(key, value) if isinstance(value, str) else (True, "")),
        TypedDictKeyTypeVerifier("pack_type", True, str),
        TypedDictKeyTypeVerifier("is_namespace", False, bool),
        TypedDictKeyTypeVerifier("suffixes", False, ListTypeVerifier(str, list, item_function=FileDataminer.suffix_function)),
        TypedDictKeyTypeVerifier("unrecognized_suffix_okay", False, bool),
        TypedDictKeyTypeVerifier("find_none_okay", False, bool),
        TypedDictKeyTypeVerifier("ignore_subdirectories", False, ListTypeVerifier(str, list, item_function=FileDataminer.location_item_function)),
        TypedDictKeyTypeVerifier("ignore_files", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("ignore_any_directories", False, ListTypeVerifier(str, list, item_function=FileDataminer.location_item_function)),
    )

    def initialize(
        self,
        location:str|Sequence[str],
        pack_type:str,
        is_namespace:bool=True, # if False, pack is base instead of namespace.
        ignore_suffixes:list[str]|None=None,
        suffixes:list[str]|None=None,
        unrecognized_suffix_okay:bool=False,
        find_none_okay:bool=False,
        ignore_subdirectories:list[str]|None=None,
        ignore_files:list[str]|None=None,
        ignore_any_directories:list[str]|None=None
    ) -> None:
        self.location = (location,) if isinstance(location, str) else location
        self.pack_type = pack_type
        self.pack_or_namespace = ["packs", "namespaces"][is_namespace]
        self.ignore_suffixes = ignore_suffixes
        self.suffixes = suffixes
        self.unrecognized_suffix_okay = unrecognized_suffix_okay
        self.find_none_okay = find_none_okay
        self.ignore_subdirectories = ignore_subdirectories
        self.ignore_files:set[str] = set(ignore_files) if ignore_files is not None else set()
        self.ignore_any_directories = ignore_any_directories

    def get_packs(self, environment:DataminerEnvironment) -> dict[str,PackTypedDict]:
        return environment.dependency_data.get(self.pack_type, self)[self.pack_or_namespace]

    def get_coverage(self, file_set:FileDataminer.FileSet, environment:DataminerEnvironment) -> set[str]:
        namespaces = list(self.get_packs(environment).keys())
        output:set[str] = set()
        for pack, location in product(namespaces, self.location):
            pack_base = pack + location
            for file_name in file_set.get_files_in(pack_base):
                relative_name = file_name.removeprefix(pack_base)
                if not (
                        (self.ignore_files is None or relative_name not in self.ignore_files)
                    and (self.ignore_subdirectories is None or not any(relative_name.startswith(ignore_directory) for ignore_directory in self.ignore_subdirectories))
                    and (self.ignore_any_directories is None or not any(ignore_directory in relative_name.split("/") for ignore_directory in self.ignore_any_directories))
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

    def get_files(self, packs:dict[str,PackTypedDict], accessor:DirectoryAccessor, environment:DataminerEnvironment) -> dict[tuple[str,str,str],bytes]:
        '''
        Returns a dict with of pack name, path relative to base, file name to the file's contents.
        '''
        pack_path_name = [(pack_path, pack["name"]) for pack_path, pack in packs.items()]
        files:dict[tuple[str,str,str],bytes] = {}
        for (pack_path, pack_name), location in product(pack_path_name, self.location):
            path_base = pack_path + location
            for file_name in accessor.get_files_in(path_base):
                should_store_file = True
                relative_name = file_name.removeprefix(path_base)
                if self.ignore_files is not None and relative_name in self.ignore_files:
                    continue
                if self.ignore_subdirectories is not None and any(relative_name.startswith(ignore_directory) for ignore_directory in self.ignore_subdirectories):
                    continue
                if self.ignore_any_directories is not None and any(ignore_directory.removesuffix("/") in relative_name.split("/") for ignore_directory in self.ignore_any_directories):
                    continue
                if self.ignore_suffixes is not None and any(relative_name.endswith(ignore_suffix) for ignore_suffix in self.ignore_suffixes):
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
                    files[pack_name, relative_name, file_name] = accessor.read(file_name)

        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str,str],bytes], environment:DataminerEnvironment) -> dict[str,dict[str,File]]:
        output:dict[str,dict[str,File]] = {}
        for (pack_name, relative_name, file_name), file_bytes in files.items():
            file_data = self.export_file(file_bytes, file_name)
            if pack_name not in output:
                output[pack_name] = {}
            output[pack_name][relative_name] = file_data
        return output

    def activate(self, environment:DataminerEnvironment) -> Any:
        packs = self.get_packs(environment)
        accessor = self.get_accessor(DirectoryAccessor)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return output
