from typing import NotRequired, TypedDict

import Dataminer.FileDataminer as FileDataminer
import Downloader.Accessor as Accessor


class ImageTypedDict(TypedDict):
    image: bytes
    json_metadata: NotRequired[bytes]
    json_metadata_file_name: NotRequired[str]

IMAGE_SUFFIXES = {"png", "jpg", "jpeg", "gif", "tga", "ttf", "webm", "svg", "otf"}
# items should contain exactly no period characters

def coverage_in_directory(directory:str, file_set:FileDataminer.FileSet, ignore_directories:list[str]|None=None) -> set[str]:
    output:set[str] = set()
    for file_name in file_set.get_files_in(directory):
        if file_name.split("/")[-1].count(".") == 0:
            continue
        relative_name = file_name.removeprefix(directory)
        if ignore_directories is not None and any(relative_name.startswith(ignore_directory) for ignore_directory in ignore_directories):
            continue
        file_without_suffix = ".".join(file_name.split(".")[:-1])
        file_suffix = file_name.split(".")[-1]
        if file_suffix not in IMAGE_SUFFIXES:
            continue
        output.add(file_name)
        json_file_path = file_without_suffix + ".json"
        if json_file_path in directory:
            output.add(json_file_path)
    return output

def get_in_directory(directory:str, accessor:Accessor.DirectoryAccessor, ignore_directories:list[str]|None=None) -> dict[str,ImageTypedDict]:
    '''
    Returns dict {full_file_name: {"image": image_metadata, "json_metadata": json_metadata}}
    '''
    output:dict[str,ImageTypedDict] = {}
    for file_name in accessor.get_files_in(directory):
        if file_name.split("/")[-1].count(".") == 0:
            continue
        relative_name = file_name.removeprefix(directory)
        if ignore_directories is not None and any(relative_name.startswith(ignore_directory) for ignore_directory in ignore_directories):
            continue
        file_without_suffix = ".".join(file_name.split(".")[:-1])
        file_suffix = file_name.split(".")[-1]
        if file_suffix not in IMAGE_SUFFIXES:
            continue
        image_dict:ImageTypedDict = {"image": accessor.read(file_name)}
        json_file_path = file_without_suffix + ".json"
        if accessor.file_exists(json_file_path):
            image_dict["json_metadata"] = accessor.read(json_file_path)
            image_dict["json_metadata_file_name"] = json_file_path
        output[file_name] = image_dict
    return output
