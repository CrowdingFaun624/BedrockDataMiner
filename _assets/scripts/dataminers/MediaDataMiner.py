from typing import Any

import _assets.scripts.dataminers.ImageDataMiner as ImageDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MediaDataMiner"]

class MediaDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=FileDataMiner.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_subdirectories", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.location_item_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    serializer_names = {"image_metadata", "json_metadata"}

    def initialize(self, location:str, find_none_okay:bool=False, ignore_subdirectories:list[str]|None=None, insert_pack:str|None=None) -> None:
        self.location = location
        self.find_none_okay = find_none_okay
        self.ignore_subdirectories = ignore_subdirectories
        self.insert_pack = insert_pack

    def get_coverage(self, file_set:FileDataMiner.FileSet, environment: DataMinerEnvironment.DataMinerEnvironment) -> set[str]:
        ignore_directories = [self.location + subdirectory for subdirectory in self.ignore_subdirectories] if self.ignore_subdirectories is not None else None
        output:set[str] = ImageDataMiner.coverage_in_directory(self.location, file_set, ignore_directories)
        if len(output) == 0 and not self.find_none_okay:
            raise Exceptions.DataMinerNothingFoundError(self)
        return output

    def get_files(self, path_base: str, accessor: Accessor.DirectoryAccessor, environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[tuple[str, str], ImageDataMiner.ImageTypedDict]:
        ignore_directories = [self.location + subdirectory for subdirectory in self.ignore_subdirectories] if self.ignore_subdirectories is not None else None
        files:dict[tuple[str,str],ImageDataMiner.ImageTypedDict] = {(file_name.removeprefix(path_base), file_name): file_data for file_name, file_data in ImageDataMiner.get_in_directory(path_base, accessor, ignore_directories).items()}
        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataMinerNothingFoundError(self)
        return files

    def get_output(self, files: dict[tuple[str, str], ImageDataMiner.ImageTypedDict], accessor: Accessor.DirectoryAccessor, environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str, Any]:
        output:dict[str,Any] = {}
        for (relative_name, file_name), files_bytes in files.items():
            files_files:dict[str,File.File|Any] = {
                "image_metadata": self.export_file(files_bytes["image"], file_name, "image_metadata")
            }
            if "json_metadata" in files_bytes:
                files_files["json_metadata"] = self.export_file(files_bytes["json_metadata"], files_bytes.get("json_metadata_file_name", ""), "")
            if self.insert_pack is None:
                output[relative_name] = files_files
            else:
                output[relative_name] = {self.insert_pack: files_files}
        return output

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        files = self.get_files(self.location, accessor, environment)
        output = self.get_output(files, accessor, environment)
        return Sorting.sort_everything(output)
