import hashlib
import shutil
import uuid
from pathlib import Path
from typing import IO

import Utilities.Exceptions as Exceptions

PARENT_DIRECTORY          = Path("./").absolute()
ASSETS_DIRECTORY          = PARENT_DIRECTORY.joinpath("_assets")
DATA_DIRECTORY            = ASSETS_DIRECTORY.joinpath("data")
FILE_STORAGE_DIRECTORY    = ASSETS_DIRECTORY.joinpath("file_storage")
FILE_STORAGE_OBJECTS_DIRECTORY = FILE_STORAGE_DIRECTORY.joinpath("objects")
FILE_STORAGE_INDEX_FILE   = FILE_STORAGE_DIRECTORY.joinpath("index.txt")
LOG_DIRECTORY             = ASSETS_DIRECTORY.joinpath("log")
LOGS_FILE                 = LOG_DIRECTORY.joinpath("logs.json")
SCRIPTS_DIRECTORY         = ASSETS_DIRECTORY.joinpath("scripts")
STORED_VERSIONS_DIRECTORY = ASSETS_DIRECTORY.joinpath("stored_versions")
STORED_VERSIONS_INPUT_DIRECTORY = STORED_VERSIONS_DIRECTORY.joinpath("input")
STORED_VERSIONS_OBJECTS_DIRECTORY = STORED_VERSIONS_DIRECTORY.joinpath("objects")
STORED_VERSIONS_OUTPUT_DIRECTORY = STORED_VERSIONS_DIRECTORY.joinpath("output")
STORED_VERSIONS_INDEXES_FILE = STORED_VERSIONS_DIRECTORY.joinpath("indexes.zip")
STRUCTURES_DIRECTORY      = ASSETS_DIRECTORY.joinpath("structures")
ACCESSOR_TYPES_FILE       = ASSETS_DIRECTORY.joinpath("accessor_types.json")
DATAMINER_COLLECTIONS_FILE = ASSETS_DIRECTORY.joinpath("dataminer_collections.json")
EXIFTOOL_CACHE            = ASSETS_DIRECTORY.joinpath("exiftool_cache.txt")
FSB_CACHE_FILE            = ASSETS_DIRECTORY.joinpath("fsb_cache.json")
MATERIAL_BIN_CACHE_FILE   = ASSETS_DIRECTORY.joinpath("material_bin_cache.txt")
SERIALIZERS_FILE          = ASSETS_DIRECTORY.joinpath("serializers.json")
STRUCTURE_TAGS_FILE       = ASSETS_DIRECTORY.joinpath("structure_tags.json")
RESOUCE_PACK_DATA_FILE    = ASSETS_DIRECTORY.joinpath("resource_pack_data.json")
TABLIFIERS_FILE           = ASSETS_DIRECTORY.joinpath("tablifiers.json")
VERSION_FILE_TYPES_FILE   = ASSETS_DIRECTORY.joinpath("version_file_types.json")
VERSION_TAGS_DIRECTORY    = ASSETS_DIRECTORY.joinpath("version_tag")
LATEST_SLOTS_FILE         = VERSION_TAGS_DIRECTORY.joinpath("latest_slots.json")
VERSION_TAGS_FILE         = VERSION_TAGS_DIRECTORY.joinpath("version_tags.json")
VERSION_TAGS_ORDER_FILE   = VERSION_TAGS_DIRECTORY.joinpath("version_tags_order.json")
VERSIONS_FILE             = ASSETS_DIRECTORY.joinpath("versions.json")
COMPARISONS_DIRECTORY     = PARENT_DIRECTORY.joinpath("_comparisons")
LIB_DIRECTORY             = PARENT_DIRECTORY.joinpath("_lib")
LIB_FSB_DIRECTORY         = LIB_DIRECTORY.joinpath("fsb")
LIB_FSB_EXE_FILE          = LIB_FSB_DIRECTORY.joinpath("fsb_aud_extr.exe")
LIB_EXIFTOOL_DIRECTORY    = LIB_DIRECTORY.joinpath("exiftool-12.93_64")
LIB_EXIFTOOL_EXE_FILE     = LIB_EXIFTOOL_DIRECTORY.joinpath("exiftool.exe")
LIB_MATERIAL_BIN_TOOL_DIRECTORY = LIB_DIRECTORY.joinpath("MaterialBinTool")
OUTPUT_DIRECTORY          = PARENT_DIRECTORY.joinpath("_output")
TEMP_DIRECTORY            = PARENT_DIRECTORY.joinpath("_temp")
VERSIONS_DIRECTORY        = PARENT_DIRECTORY.joinpath("_versions")

def get_comparison_file_path(name:str, number:int|None=None) -> Path:
    if number is None:
        comparison_path = COMPARISONS_DIRECTORY.joinpath(name)
    else:
        comparison_path = COMPARISONS_DIRECTORY.joinpath(name, "report_%s.txt" % str(number).zfill(4))
    if COMPARISONS_DIRECTORY not in comparison_path.parents:
        raise Exceptions.InvalidFileNameError(name, "Comparison", "(%i)" % (number,))
    return comparison_path

def get_file_size(io:IO) -> int: # https://stackoverflow.com/questions/6591931/getting-file-size-in-python
    start = io.tell()
    io.seek(0,2) # move the cursor to the end of the file
    size = io.tell()
    io.seek(start)
    return size

def get_structure_path(structure_name:str) -> Path:
    structure_path = STRUCTURES_DIRECTORY.joinpath(structure_name + ".json")
    if STRUCTURES_DIRECTORY not in structure_path.parents:
        raise Exceptions.InvalidFileNameError(structure_name, "Structure")
    return structure_path

def get_version_path(version_name:str) -> Path:
    version_path = VERSIONS_DIRECTORY.joinpath(version_name)
    if VERSIONS_DIRECTORY not in version_path.parents:
        raise Exceptions.InvalidFileNameError(version_name, "Version")
    return version_path

def get_data_file_path(file_name:str) -> Path:
    data_file_path = DATA_DIRECTORY.joinpath(file_name)
    if DATA_DIRECTORY not in data_file_path.parents:
        raise Exceptions.InvalidFileNameError(file_name, "Structure")
    return data_file_path

def get_version_install_path(version_directory:Path) -> Path:
    return version_directory.joinpath("client")

def get_version_data_path(version_directory:Path, file_name:str|None) -> Path:
    '''Returns the Path in the version directory that a data file name will be stored at. Set `file_name` to None to get the data path.'''
    if file_name is None:
        data_path = version_directory.joinpath("./data")
    else:
        data_path = version_directory.joinpath("./data/%s" % file_name)
    if version_directory not in data_path.parents:
        raise Exceptions.InvalidFileNameError(data_path.name, "Data file")
    if VERSIONS_DIRECTORY != version_directory.parent:
        raise Exceptions.InvalidFileNameError(data_path.name, "Data file")
    return data_path

def get_version_index_path(version_directory:Path) -> Path:
    return version_directory.joinpath("index.json")

def get_temp_file_path() -> Path:
    '''Returns a path such as `./_temp/a6f780a3-83d0-4afd-a654-dc28df0b9831`.'''
    return TEMP_DIRECTORY.joinpath(str(uuid.uuid4()))

def stringify_sha1_hash(sha1_hash:bytes) -> str:
    '''
    Returns a hexadecimal string with length 40.
    '''
    return hex(int.from_bytes(sha1_hash, "big"))[2:].zfill(40)

def get_hash(file:IO) -> bytes:
    '''
    Returns the sha1 hash of a file opened in binary mode.
    '''
    BUFFER_SIZE = 65536 # 64kb
    sha1_hash = hashlib.sha1()
    while True:
        data = file.read(BUFFER_SIZE)
        if not data: break
        sha1_hash.update(data)
    return sha1_hash.digest()

def get_hash_bytes(file:bytes) -> bytes:
    '''
    Returns the sha1 hash of bytes.
    '''
    return hashlib.sha1(file).digest()

def clear_temp() -> None:
    '''
    Removes every file and recursively removes every directory from the temp directory.
    '''
    for file in TEMP_DIRECTORY.iterdir():
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

clear_temp()
