import errno
import hashlib
import os
import shutil
import sys
import uuid
from typing import IO, Any, Callable, Literal

from pathlib2 import Path

from Utilities.FunctionCaller import FunctionCaller

PARENT_FOLDER          = Path("./").absolute()
ASSETS_FOLDER          = PARENT_FOLDER.joinpath("_assets")
FILE_STORAGE_FOLDER    = ASSETS_FOLDER.joinpath("file_storage")
FILE_STORAGE_OBJECTS_FOLDER = FILE_STORAGE_FOLDER.joinpath("objects")
FILE_STORAGE_INDEX_FILE = FILE_STORAGE_FOLDER.joinpath("index.txt")
LOGS_FOLDER            = ASSETS_FOLDER.joinpath("logs")
DOWNLOAD_LOG           = LOGS_FOLDER.joinpath("download_log.jsonl")
VERSION_PARSER_WARNINGS_FILE = LOGS_FOLDER.joinpath("version_parser_warnings.txt")
WIKI_VALIDATOR_WARNINGS_FILE = LOGS_FOLDER.joinpath("wiki_validator_warnings.txt")
SCRIPTS_FOLDER         = ASSETS_FOLDER.joinpath("scripts")
STORED_VERSIONS_FOLDER = ASSETS_FOLDER.joinpath("stored_versions")
STORED_VERSIONS_INPUT_FOLDER = STORED_VERSIONS_FOLDER.joinpath("input")
STORED_VERSIONS_OBJECTS_FOLDER = STORED_VERSIONS_FOLDER.joinpath("objects")
STORED_VERSIONS_OUTPUT_FOLDER = STORED_VERSIONS_FOLDER.joinpath("output")
STORED_VERSIONS_INDEXES_FILE = STORED_VERSIONS_FOLDER.joinpath("indexes.zip")
STRUCTURES_FOLDER      = ASSETS_FOLDER.joinpath("structures")
ACCESSOR_TYPES_FILE         = ASSETS_FOLDER.joinpath("accessor_types.json")
DATAMINER_COLLECTIONS_FILE = ASSETS_FOLDER.joinpath("dataminer_collections.json")
FSB_CACHE_FILE         = ASSETS_FOLDER.joinpath("fsb_cache.json")
RESOUCE_PACK_DATA_FILE = ASSETS_FOLDER.joinpath("resource_pack_data.json")
STRUCTURES_FILE        = ASSETS_FOLDER.joinpath("structures.json")
VERSION_FILE_TYPES_FILE= ASSETS_FOLDER.joinpath("version_file_types.json")
VERSION_TAGS_FILE      = ASSETS_FOLDER.joinpath("version_tags.json")
VERSIONS_FILE          = ASSETS_FOLDER.joinpath("versions.json")
COMPARISONS_FOLDER     = PARENT_FOLDER.joinpath("_comparisons")
LIB_FOLDER             = PARENT_FOLDER.joinpath("_lib")
LIB_FSB_FOLDER         = LIB_FOLDER.joinpath("fsb")
LIB_FSB_EXE_FILE       = LIB_FSB_FOLDER.joinpath("fsb_aud_extr.exe")
TEMP_FOLDER            = PARENT_FOLDER.joinpath("_temp")
VERSIONS_FOLDER        = PARENT_FOLDER.joinpath("_versions")

def get_comparison_file_path(name:str, number:int|None=None) -> Path:
    if number is None:
        comparison_path = Path(COMPARISONS_FOLDER.joinpath(name))
    else:
        comparison_path = Path(COMPARISONS_FOLDER.joinpath(name, "report_%s.txt" % str(number).zfill(4)))
    if COMPARISONS_FOLDER not in comparison_path.parents:
        raise FileNotFoundError("Comparison \"%s\" (%i)'s folder can not be created due to illegal characters!" % (name, number))
    return comparison_path

def get_file_size(io:IO) -> int: # https://stackoverflow.com/questions/6591931/getting-file-size-in-python
    start = io.tell()
    io.seek(0,2) # move the cursor to the end of the file
    size = io.tell()
    io.seek(start)
    return size

def get_structure_path(structure_name:str) -> Path:
    structure_path = Path(STRUCTURES_FOLDER.joinpath(structure_name + ".json"))
    if STRUCTURES_FOLDER not in structure_path.parents:
        raise FileNotFoundError("Structure \"%s\" can not be created due to illegal characters!" % structure_name)
    return structure_path

def get_version_path(version_name:str) -> Path:
    version_path = Path(VERSIONS_FOLDER.joinpath(version_name))
    if VERSIONS_FOLDER not in version_path.parents:
        raise FileNotFoundError("Version \"%s\"'s folder can not be created due to illegal characters!" % version_name)
    return version_path

def get_version_install_path(version_folder:Path) -> Path:
    return Path(version_folder.joinpath("client"))

def get_version_data_path(version_folder:Path, file_name:str|None) -> Path:
    '''Returns the Path in the version folder that a data file name will be stored at. Set `file_name` to None to get the data path.'''
    if file_name is None:
        data_path = Path(version_folder.joinpath("./data"))
    else:
        data_path = Path(version_folder.joinpath("./data/%s" % file_name))
    if version_folder not in data_path.parents:
        raise FileNotFoundError("Data file \"%s\" has an invalid name!" % file_name)
    if VERSIONS_FOLDER != version_folder.parent:
        raise FileNotFoundError("Version folder \"%s\" has an invalid location!" % version_folder)
    return data_path

def get_version_index_path(version_folder:Path) -> Path:
    return Path(version_folder.joinpath("index.json"))

def get_temp_file_path() -> Path:
    '''Returns a path such as `./_temp/a6f780a3-83d0-4afd-a654-dc28df0b9831`.'''
    return Path(TEMP_FOLDER.joinpath(str(uuid.uuid4())))

def is_pathname_valid(pathname:str) -> bool: # https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
    '''
    Returns True if the path name is valid on this OS.
    '''
    ERROR_INVALID_NAME = 123
    try:
        if not isinstance(pathname, str) or not pathname:
            return False
        _, pathname = os.path.splitdrive(pathname)
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError as exc:
        return False
    else:
        return True

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
    Removes every file and recursively removes every folder from the temp directory.
    '''
    for file in TEMP_FOLDER.iterdir():
        file:Path
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
            raise RuntimeError("Attempted to open FilePromise \"%s\" that has been marked as all done!" % self.name)
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
