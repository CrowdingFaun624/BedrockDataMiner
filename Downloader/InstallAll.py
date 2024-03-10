import datetime
import json
from pathlib2 import Path
import traceback
from typing import TypedDict, Union

import Downloader.VersionsParser as VersionsParser
import Utilities.FileManager as FileManager
import Utilities.StoredVersionsManager2 as StoredVersionsManager
import Utilities.Version as Version

JsonableType = dict[str,Union["JsonableType",list[str]]]|list["JsonableType"]|str|int|float|bool|None

class IndexTypedDict(TypedDict):
    sha1: str
    z: int

def reset_log() -> None:
    with open(FileManager.INSTALL_ALL_LOGS_FILE, "wt") as f:
        f.write("")

def write_to_log(data:JsonableType) -> None:
    stringified_data = json.dumps(data)
    with open(FileManager.INSTALL_ALL_LOGS_FILE, "at") as f:
        f.write(stringified_data + "\n")

def store_index(index:dict[str,IndexTypedDict], version:Version.Version) -> None:
    if version.version_folder is None:
        raise FileNotFoundError("Version \"%s\" has no version folder!" % (version))
    with open(FileManager.get_version_index_path(version.version_folder), "wt") as f:
        json.dump(index, f, separators=(",", ":"))

def read_index(version:Version.Version) -> dict[str,IndexTypedDict]:
    if version.version_folder is None:
        raise FileNotFoundError("Version \"%s\" has no version folder!" % (version))
    index_path = FileManager.get_version_index_path(version.version_folder)
    if not index_path.exists():
        raise FileNotFoundError("Version \"%s\" does not have an index!" % (version.name))
    with open(index_path, "rt") as f:
        return json.load(f)

def all_versions() -> None:
    reset_log()
    versions = list(reversed(VersionsParser.versions.get()))
    for version in versions:
        print(version)
        if version.install_manager is None:
            write_to_log({"timestamp": datetime.datetime.now().isoformat(), "version": version.name, "message": "Skipped due to no archived version available"})
            continue
        if version.version_folder is None:
            raise FileNotFoundError("Version \"%s\" has no version folder!" % (version))
        index_path = FileManager.get_version_index_path(version.version_folder)
        if index_path.exists():
            write_to_log({"timestamp": datetime.datetime.now().isoformat(), "version": version.name, "message": "Skipped due to already being archived"})
            version.install_manager.all_done()
            continue
        index:dict[str,IndexTypedDict] = {}
        try:
            all_files = version.install_manager.get_full_file_list()
            if len(all_files) == 0:
                raise RuntimeError("No files found!")
        except Exception as e:
            write_to_log({"timestamp": datetime.datetime.now().isoformat(), "version": version.name, "exception": traceback.format_exception(e)})
            raise RuntimeError("Failed to get file list of version \"%s\"" % (version.name))
        for file_name in all_files:
            try:
                file_hash, is_zipped = StoredVersionsManager.archive(version.install_manager.get_file(file_name, "b", is_in_assets=False))
                index[file_name] = {"sha1": file_hash, "z": int(is_zipped)}
            except Exception as e:
                write_to_log({"timestamp": datetime.datetime.now().isoformat(), "version": version.name, "exception": traceback.format_exception(e)})
                raise RuntimeError("Failed to archive version \"%s\"!" % (version.name))
        store_index(index, version)
        write_to_log({"timestamp": datetime.datetime.now().isoformat(), "version": version.name, "message": "successfully archived version"})
        version.install_manager.all_done()

def extract_version(version:Version.Version) -> None:
    if version.version_folder is None:
        raise FileNotFoundError("Version \"%s\" has no version folder!" % (version))
    destination = Path(version.version_folder.joinpath("client_extracted.zip"))
    index = read_index(version)
    StoredVersionsManager.extract(index, destination)

def difference_user_interface() -> None:
    version1 = select_version_user_interface()
    version2 = select_version_user_interface()
    if version1 == version2:
        raise RuntimeError("Cannot select the same version!")
    index1 = read_index(version1)
    index2 = read_index(version2)

    different_files:list[tuple[str,str,int]] = []
    size_difference = 0

    for file_name, file_properties1 in index1.items():
        file_hash1 = file_properties1["sha1"]
        if file_name in index2:
            file_properties2 = index2[file_name]
            file_hash2 = file_properties2["sha1"]
            if file_hash1 != file_hash2:
                size = StoredVersionsManager.get_size(file_hash1)
                different_files.append(("different", file_name, size))
                size_difference += size
        else:
            size = StoredVersionsManager.get_size(file_hash1)
            different_files.append(("unique to 1", file_name, size))
            size_difference += size
    for file_name, file_properties2 in index2.items():
        file_hash2 = file_properties2["sha1"]
        if file_name not in index1:
            size = StoredVersionsManager.get_size(file_hash2)
            different_files.append(("unique to 2", file_name, size))
            size_difference += size
    sorted_files = sorted(different_files, key=lambda value: value[2], reverse=True)
    for i in range(min(50, len(sorted_files))):
        where, name, size = sorted_files[i]
        print("File %s \"%s\" %i bytes" % (where, name, size))
    print("\n%i different files, %i bytes total" % (len(sorted_files), size_difference))

def select_version_user_interface() -> Version.Version:
    versions = VersionsParser.versions_dict.get()
    user_input = None
    while user_input not in versions:
        user_input = input("Select a version to extract: ")
    return versions[user_input]

def clear_all():
    for folder in FileManager.STORED_VERSIONS2_OBJECTS_FOLDER.iterdir():
        for file in folder.iterdir():
            file.unlink()
        folder.rmdir()

def clear_all_user_interface() -> None:
    required_message = "I wish to clear all files"
    user_input = input("Enter: \"%s\"" % required_message)
    if user_input == required_message:
        clear_all()

def extract_user_interface() -> None:
    version = select_version_user_interface()
    extract_version(version)

def size_user_interface() -> None:
    total_size = StoredVersionsManager.get_total_size()
    if total_size < 2**10:
        formatted_size = "%i bytes" % total_size
    elif total_size < 2**20:
        formatted_size = "%.2f kibibytes" % (total_size / 2**10)
    elif total_size < 2**30:
        formatted_size = "%.2f mebibytes" % (total_size / 2**20)
    else:
        formatted_size = "%.2f gibibytes" % (total_size / 2**30)
    print("Total size: %i bytes (%s)" % (total_size, formatted_size))

def main() -> None:
    PROGRAMS = {
        "all_versions": all_versions,
        "clear_all": clear_all_user_interface,
        "difference": difference_user_interface,
        "extract": extract_user_interface,
        "size": size_user_interface,
    }
    user_input = None
    while user_input not in PROGRAMS:
        user_input = input("Choose a program (%s):\n" % str(list(PROGRAMS.keys())))
    PROGRAMS[user_input]()
