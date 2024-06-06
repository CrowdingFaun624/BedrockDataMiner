import hashlib
import shutil
import uuid
from typing import IO, Any, Callable, Literal

from pathlib2 import Path

import Utilities.Exceptions as Exceptions
from Utilities.FunctionCaller import FunctionCaller

PARENT_DIRECTORY          = Path("./").absolute()
ASSETS_DIRECTORY          = PARENT_DIRECTORY.joinpath("_assets")
FILE_STORAGE_DIRECTORY    = ASSETS_DIRECTORY.joinpath("file_storage")
FILE_STORAGE_OBJECTS_DIRECTORY = FILE_STORAGE_DIRECTORY.joinpath("objects")
FILE_STORAGE_INDEX_FILE   = FILE_STORAGE_DIRECTORY.joinpath("index.txt")
LOGS_DIRECTORY            = ASSETS_DIRECTORY.joinpath("logs")
DOWNLOAD_LOG              = LOGS_DIRECTORY.joinpath("download_log.jsonl")
VERSION_PARSER_WARNINGS_FILE = LOGS_DIRECTORY.joinpath("version_parser_warnings.txt")
WIKI_VALIDATOR_WARNINGS_FILE = LOGS_DIRECTORY.joinpath("wiki_validator_warnings.txt")
SCRIPTS_DIRECTORY         = ASSETS_DIRECTORY.joinpath("scripts")
STORED_VERSIONS_DIRECTORY = ASSETS_DIRECTORY.joinpath("stored_versions")
STORED_VERSIONS_INPUT_DIRECTORY = STORED_VERSIONS_DIRECTORY.joinpath("input")
STORED_VERSIONS_OBJECTS_DIRECTORY = STORED_VERSIONS_DIRECTORY.joinpath("objects")
STORED_VERSIONS_OUTPUT_DIRECTORY = STORED_VERSIONS_DIRECTORY.joinpath("output")
STORED_VERSIONS_INDEXES_FILE = STORED_VERSIONS_DIRECTORY.joinpath("indexes.zip")
STRUCTURES_DIRECTORY      = ASSETS_DIRECTORY.joinpath("structures")
ACCESSOR_TYPES_FILE       = ASSETS_DIRECTORY.joinpath("accessor_types.json")
DATAMINER_COLLECTIONS_FILE = ASSETS_DIRECTORY.joinpath("dataminer_collections.json")
FSB_CACHE_FILE            = ASSETS_DIRECTORY.joinpath("fsb_cache.json")
RESOUCE_PACK_DATA_FILE    = ASSETS_DIRECTORY.joinpath("resource_pack_data.json")
VERSION_FILE_TYPES_FILE   = ASSETS_DIRECTORY.joinpath("version_file_types.json")
VERSION_TAGS_FILE         = ASSETS_DIRECTORY.joinpath("version_tags.json")
VERSIONS_FILE             = ASSETS_DIRECTORY.joinpath("versions.json")
COMPARISONS_DIRECTORY     = PARENT_DIRECTORY.joinpath("_comparisons")
LIB_DIRECTORY             = PARENT_DIRECTORY.joinpath("_lib")
LIB_FSB_DIRECTORY         = LIB_DIRECTORY.joinpath("fsb")
LIB_FSB_EXE_FILE          = LIB_FSB_DIRECTORY.joinpath("fsb_aud_extr.exe")
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

def get_hash_from_bytes(data:bytes) -> bytes:
    '''
    Returns the sha1 hash of a bytes object.
    '''
    sha1_hash = hashlib.sha1()
    data_length = len(data)
    BUFFER_SIZE = 65536
    for i in range(0, data_length, BUFFER_SIZE):
        if i + BUFFER_SIZE >= data_length:
            sha1_hash.update(data[i:])
        else:
            sha1_hash.update(data[i:i+BUFFER_SIZE])
    return sha1_hash.digest()

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

def clear_temp() -> None:
    '''
    Removes every file and recursively removes every directory from the temp directory.
    '''
    for file in TEMP_DIRECTORY.iterdir():
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

class FilePromise():
    '''An abstraction for a file that can return an IO object multiple times with FilePromise.open()'''

    def __init__(self, open_callable:FunctionCaller[IO], name:str, mode:Literal["b", "t"], all_done_callable:FunctionCaller|Callable[[],Any]|None=None) -> None:
        '''
        :open_callable: Function that takes no arguments and returns an IO object.
        :name: Name of the file, but has no real meaning.
        :mode: Describes if the IO returned by open_callable is in binary or text mode.
        :all_done_callable: Function that takes no arguments and cleans up everything related to the file.
        '''

        self.open_callable = open_callable
        self.all_done_callable = all_done_callable
        self.name = name
        self.mode = mode
        self.is_all_done = False

    def open(self) -> IO:
        '''
        Calls open_callable used to create this FilePromise and returns its IO object.
        Cannot be called if `all_done` has been called on this FilePromise.
        '''
        if self.is_all_done:
            raise Exceptions.OpenAllDoneFilePromiseError(self)
        return self.open_callable()

    def all_done(self) -> None:
        '''
        Cleans up everything related to the file.
        Cannot be opened again afte rthis is called.
        '''
        self.is_all_done = True
        if self.all_done_callable is not None:
            self.all_done_callable()

    def __repr__(self) -> str:
        return "<FilePromise %s in %s>" % (self.name, self.mode)

clear_temp()
