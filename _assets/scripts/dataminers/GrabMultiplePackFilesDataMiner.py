from typing import Any, Literal

import _assets.scripts.dataminers.PacksDataMiner as PacksDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["GrabMultiplePackFilesDataMiner"]

class GrabMultiplePackFilesDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=FileDataMiner.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("pack_type", "a str", True, TypeVerifier.EnumTypeVerifier(("resource_packs", "behavior_packs"))),
        TypeVerifier.TypedDictKeyTypeVerifier("suffixes", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.suffix_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("unrecognized_suffix_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
    )

    def initialize(
        self,
        location:str,
        pack_type:Literal["resource_packs", "behavior_packs"],
        ignore_suffixes:list[str]|None=None,
        suffixes:list[str]|None=None,
        unrecognized_suffix_okay:bool=False,
        find_none_okay:bool=False,
    ) -> None:
        self.location = location
        self.pack_type = pack_type
        self.ignore_suffixes = ignore_suffixes
        self.suffixes = suffixes
        self.unrecognized_suffix_okay = unrecognized_suffix_okay
        self.find_none_okay = find_none_okay

    def get_packs(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[PacksDataMiner.PackTypedDict]:
        return environment.dependency_data.get(self.pack_type, self)

    def get_files(self, packs:list[PacksDataMiner.PackTypedDict], accessor:Accessor.DirectoryAccessor, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[tuple[str,str,str],bytes]:
        '''
        Returns a dict with of pack name, path relative to base, file name to the file's contents.
        '''
        files:dict[tuple[str,str,str],bytes] = {}
        for pack in packs:
            path_base = pack["path"] + self.location
            for file_name in accessor.get_files_in(path_base):
                should_store_file = True
                if self.ignore_suffixes is not None and any(file_name.endswith(ignore_suffix) for ignore_suffix in self.ignore_suffixes):
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
                    files[pack["name"], relative_name, file_name] = accessor.read(file_name, "b")

        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataMinerNothingFoundError(self)
        return files

    def get_output(self, files:dict[tuple[str,str,str],bytes], environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,dict[str,Any]]:
        output:dict[str,dict[str,Any]] = {}
        for (pack_name, relative_name, file_name), file_bytes in files.items():
            file_data = self.export_file(file_bytes, file_name)
            if relative_name not in output:
                output[relative_name] = {}
            output[relative_name][pack_name] = file_data
        return output

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        packs = environment.dependency_data.get(self.pack_type, self)
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        files = self.get_files(packs, accessor, environment)
        output = self.get_output(files, environment)
        return Sorting.sort_everything(output)
