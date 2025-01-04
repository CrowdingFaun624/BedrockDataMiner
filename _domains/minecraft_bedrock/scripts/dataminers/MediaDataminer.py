from typing import Any

import _domains.minecraft_bedrock.scripts.dataminers.ImageDataminer as ImageDataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Downloader.DirectoryAccessor as DirectoryAccessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["MediaDataminer"]

class MediaDataminer(FileDataminer.FileDataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str, function=FileDataminer.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("find_none_okay", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_subdirectories", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataminer.location_item_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("insert_pack", "a str", False, str),
    )

    serializer_names = {"image_metadata", "json_metadata"}

    def initialize(self, location:str, find_none_okay:bool=False, ignore_subdirectories:list[str]|None=None, insert_pack:str|None=None) -> None:
        self.location = location
        self.find_none_okay = find_none_okay
        self.ignore_subdirectories = ignore_subdirectories
        self.insert_pack = insert_pack

    def get_coverage(self, file_set:FileDataminer.FileSet, environment: DataminerEnvironment.DataminerEnvironment) -> set[str]:
        ignore_directories = [self.location + subdirectory for subdirectory in self.ignore_subdirectories] if self.ignore_subdirectories is not None else None
        output:set[str] = ImageDataminer.coverage_in_directory(self.location, file_set, ignore_directories)
        if len(output) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return output

    def get_files(self, path_base: str, accessor: DirectoryAccessor.DirectoryAccessor, environment: DataminerEnvironment.DataminerEnvironment) -> dict[tuple[str, str], ImageDataminer.ImageTypedDict]:
        ignore_directories = [self.location + subdirectory for subdirectory in self.ignore_subdirectories] if self.ignore_subdirectories is not None else None
        files:dict[tuple[str,str],ImageDataminer.ImageTypedDict] = {(file_name.removeprefix(path_base), file_name): file_data for file_name, file_data in ImageDataminer.get_in_directory(path_base, accessor, ignore_directories).items()}
        if len(files) == 0 and not self.find_none_okay:
            raise Exceptions.DataminerNothingFoundError(self)
        return files

    def get_output(self, files: dict[tuple[str, str], ImageDataminer.ImageTypedDict], accessor: DirectoryAccessor.DirectoryAccessor, environment: DataminerEnvironment.DataminerEnvironment) -> dict[str, Any]:
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

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> Any:
        accessor = self.get_accessor(DirectoryAccessor.DirectoryAccessor)
        files = self.get_files(self.location, accessor, environment)
        output = self.get_output(files, accessor, environment)
        return output
