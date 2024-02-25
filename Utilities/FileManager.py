import errno
import hashlib
import os
from pathlib2 import Path
import shutil
import sys
import threading
from typing import Any, Callable, IO, Literal
import uuid

from Utilities.FunctionCaller import FunctionCaller

PARENT_FOLDER          = Path("./").absolute()
ASSETS_FOLDER          = Path(PARENT_FOLDER.joinpath("_assets"))
COMPARERS_FOLDER       = Path(ASSETS_FOLDER.joinpath("comparers"))
FILE_STORAGE_FOLDER    = Path(ASSETS_FOLDER.joinpath("file_storage"))
FILE_STORAGE_OBJECTS_FOLDER = Path(FILE_STORAGE_FOLDER.joinpath("objects"))
FILE_STORAGE_INDEX_FILE = Path(FILE_STORAGE_FOLDER.joinpath("index.txt"))
LOGS_FOLDER            = Path(ASSETS_FOLDER.joinpath("logs"))
VERSION_PARSER_WARNINGS_FILE = Path(LOGS_FOLDER.joinpath("version_parser_warnings.txt"))
WIKI_VALIDATOR_WARNINGS_FILE = Path(LOGS_FOLDER.joinpath("wiki_validator_warnings.txt"))
STORED_VERSIONS_FOLDER = Path(ASSETS_FOLDER.joinpath("stored_versions"))
STORED_VERSIONS_OBJECTS_FOLDER = Path(STORED_VERSIONS_FOLDER.joinpath("objects"))
STORED_VERSIONS_INDEXES_FILE = Path(STORED_VERSIONS_FOLDER.joinpath("indexes.zip"))
STORED_VERSIONS_INPUT_FOLDER = Path(STORED_VERSIONS_FOLDER.joinpath("input"))
STORED_VERSIONS_OUTPUT_FOLDER = Path(STORED_VERSIONS_FOLDER.joinpath("output"))
COMPARERS_FILE         = Path(ASSETS_FOLDER.joinpath("comparers.json"))
DATAMINER_COLLECTIONS_FILE = Path(ASSETS_FOLDER.joinpath("dataminer_collections.json"))
VERSIONS_FILE          = Path(ASSETS_FOLDER.joinpath("versions.json"))
FSB_CACHE_FILE         = Path(ASSETS_FOLDER.joinpath("fsb_cache.json"))
RESOUCE_PACK_DATA_FILE      = Path(ASSETS_FOLDER.joinpath("resource_pack_data.json"))
COMPARISONS_FOLDER     = Path(PARENT_FOLDER.joinpath("_comparisons"))
LIB_FOLDER             = Path(PARENT_FOLDER.joinpath("_lib"))
LIB_FSB_FOLDER         = Path(LIB_FOLDER.joinpath("fsb"))
LIB_FSB_EXE_FILE       = Path(LIB_FSB_FOLDER.joinpath("fsb_aud_extr.exe"))
TEMP_FOLDER            = Path(PARENT_FOLDER.joinpath("_temp"))
VERSIONS_FOLDER        = Path(PARENT_FOLDER.joinpath("_versions"))

opened_shared_files:dict[Path,threading.Lock] = {}

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

def get_comparer_path(comparer_name:str) -> Path:
    comparer_path = Path(COMPARERS_FOLDER.joinpath(comparer_name + ".json"))
    if COMPARERS_FOLDER not in comparer_path.parents:
        raise FileNotFoundError("Comparer \"%s\" can not be created due to illegal characters!" % comparer_name)
    return comparer_path

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

def get_temp_file_path() -> Path:
    '''Returns a path such as `./_temp/a6f780a3-83d0-4afd-a654-dc28df0b9831`.'''
    return Path(TEMP_FOLDER.joinpath(str(uuid.uuid4())))

def open_shared_file(path:Path, mode:str="r", *args, **kwargs) -> IO:
    if path not in opened_shared_files:
        opened_shared_files[path] = threading.Lock()
    opened_shared_files[path].acquire()
    try:
        open_file = open(path, mode, *args, **kwargs)
    finally:
        opened_shared_files[path].release()
    return open_file

def is_pathname_valid(pathname:str) -> bool: # https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
    '''Returns True if the path name is valid on this OS.'''
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
    '''Returns a hexadecimal string with length 40.'''
    return hex(int.from_bytes(sha1_hash, "big"))[2:].zfill(40)

def get_hash(file:IO) -> bytes:
    '''Returns the sha1 hash of a file opened in binary mode.'''
    BUFFER_SIZE = 65536 # 64kb
    sha1_hash = hashlib.sha1()
    while True:
        data = file.read(BUFFER_SIZE)
        if not data: break
        sha1_hash.update(data)
    return sha1_hash.digest()

def clear_temp() -> None:
    for file in TEMP_FOLDER.iterdir():
        file:Path
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

class FilePromise():
    '''An abstraction for a file that can return an IO object multiple times with FilePromise.open()'''

    def __init__(self, open_callable:FunctionCaller[IO], name:str, mode:Literal["b", "t"], all_done_callable:FunctionCaller|Callable[[],Any]|None=None) -> None:
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        if len(name) == 0:
            raise ValueError("`name` is empty!")
        if "/" in name or "\\" in name:
            raise ValueError("`name` cannot have a \"/\" or \"\\\" character: \"%s\"" % name)
        if not isinstance(mode, str):
            raise TypeError("`mode` is not a str!")
        if mode not in ("t", "b"):
            raise ValueError("`mode` is not \"t\" or \"b\"!")

        self.open_callable = open_callable
        self.all_done_callable = all_done_callable
        self.name = name
        self.mode = mode
        self.is_all_done = False

    def open(self) -> IO:
        if self.is_all_done:
            raise RuntimeError("Attempted to open FilePromise \"%s\" that has been marked as all done!" % self.name)
        return self.open_callable()

    def all_done(self) -> None:
        self.is_all_done = True
        if self.all_done_callable is not None:
            self.all_done_callable()

    def __repr__(self) -> str:
        return "<FilePromise %s in %s>" % (self.name, self.mode)

clear_temp()
