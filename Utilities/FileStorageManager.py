import gzip
from typing import IO, Literal, overload

from pathlib2 import Path

import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller

COMPRESSIBLE_FILES = ["json", "fsb", "txt", "lang", "tga", "xml", "bin", "fragment", "h", "vertex", "properties", "material", "ttf", "otf", "fontdata", "css", "js", "html", "dat", "wlist", "pdn", "so", "dex", "sf", "mf"]

CACHE_LIMIT = 2 # how many times it has to miss the cache in order to cache the file.

cache_counts:dict[str,int] = {}
cache_data:dict[str,bytes|str] = {}

def read_index() -> dict[str, tuple[bool, str]]:
    '''Returns a dictionary of hex string hashes, and the file's zippability and a name it has.
    Should only be called once at the start of the program, and then the `index` variable should be used.'''
    with open(FileManager.FILE_STORAGE_INDEX_FILE, "rt") as index_file_io:
        index_lines = index_file_io.readlines()
    return {line[:40]: (bool(int(line[41])), line[43:].rstrip()) for line in index_lines}

index = read_index()

def reopen_in_binary(file:FileManager.FilePromise) -> FileManager.FilePromise:
    '''Returns a new FilePromise in binary mode if the current one is in text mode.'''
    if file.mode == "t":
        temp_file_path = FileManager.get_temp_file_path()
        with open(temp_file_path, "wt") as temp_file, file.open() as file_io:
            temp_file.write(file_io.read())
        return FileManager.FilePromise(FunctionCaller(open, [temp_file_path, "rb"]), file.name, "b", temp_file_path.unlink)
    else: return file

def should_zip_file(file:FileManager.FilePromise) -> bool:
    '''Returns if the file is efficiently zippable.'''
    file_name = file.name.split("/")[-1].split("\\")[-1]
    file_end = file_name.split(".")[-1].lower() if "." in file_name else ""
    return file_end in COMPRESSIBLE_FILES

def get_file_path(hex_string:str) -> Path:
    archived_directory = FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.joinpath(hex_string[:2])
    archived_path = archived_directory.joinpath(hex_string)
    return archived_path

def archive_data(data:bytes|str, file_name:str) -> str:
    temp_file = FileManager.get_temp_file_path()
    file_mode = "b" if isinstance(data, bytes) else "t"
    with open(temp_file, "w" + file_mode) as f:
        f.write(data) # copying it so I can read it multiple times.
    return_value = archive(FileManager.FilePromise(FunctionCaller(open, [temp_file, "rb"]), file_name, "b"))
    temp_file.unlink()
    return return_value

def archive(file:FileManager.FilePromise) -> str:
    '''Takes in a FilePromise object, and stores a file in the `./_assets/file_storage/objects` directory, and adds its data to the `./_assets/file_storage/index.txt` file.
    Returns the sha1 hash in a hexadecimal string format that the file is stored at.
    If the file already exists in the archive, do nothing.'''
    file = reopen_in_binary(file)
    file_hash = FileManager.get_hash(file.open())
    hex_string = FileManager.stringify_sha1_hash(file_hash)
    archived_directory = FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.joinpath(hex_string[:2])
    archived_path = get_file_path(hex_string)
    archived_directory.mkdir(exist_ok=True)
    zipped = should_zip_file(file)
    with open(archived_path, "wb") as destination, file.open() as source:
        if FileManager.get_file_size(source) == 0:
            raise ValueError("File \"%s\" returned an IO object with length 0!" % file.name)
        if zipped:
            destination.write(gzip.compress(source.read()))
        else:
            destination.write(source.read())

    with open(FileManager.FILE_STORAGE_INDEX_FILE, "at") as index_file:
        index_file.write("%s %i %s\n" % (hex_string, zipped, file.name))
    index[hex_string] = (zipped, file.name)

    return hex_string

def archive_io(file:IO, file_name:str) -> str:
    '''Takes in a binary IO object, and stores a file in the `./_assets/file_storage/objects` directory, and adds its data to the `./_assets/file_storage/index.txt` file.
    Returns the sha1 hash in a hexadecimal string format that the file is stored at.
    If the file already exists in the archive, do nothing.'''
    temp_file = FileManager.get_temp_file_path()
    with open(temp_file, "wb") as f:
        f.write(file.read()) # copying it so I can read it multiple times.
    return_value = archive(FileManager.FilePromise(FunctionCaller(open, [temp_file, "rb"]), file_name, "b"))
    temp_file.unlink()
    return return_value

def open_archived(hex_string:str, mode:Literal["t", "b"]) -> FileManager.FilePromise:
    archived_path = get_file_path(hex_string)
    if not archived_path.exists():
        raise FileNotFoundError("File with hash \"%s\" does not exist!" % hex_string)
    is_zipped, name = index[hex_string]
    if is_zipped:
        temp_file = FileManager.get_temp_file_path()
        with open(archived_path, "rb") as f, open(temp_file, "wb") as temp_file_io:
            temp_file_io.write(gzip.decompress(f.read()))
        return FileManager.FilePromise(FunctionCaller(open, [temp_file, "r" + mode]), temp_file.name, "b", temp_file.unlink)
    else:
        return FileManager.FilePromise(FunctionCaller(open, [archived_path, "r" + mode]), hex_string, "b")

@overload
def read_archived(hex_string:str, mode:Literal["b"]) -> bytes: ...
@overload
def read_archived(hex_string:str, mode:Literal["t"]) -> str: ...
def read_archived(hex_string:str, mode:Literal["t", "b"]) -> bytes|str:
    cache_name = hex_string + "-" + mode
    cached_file = cache_data.get(cache_name)
    if cached_file is not None:
        return cached_file
    try:
        cache_counts[cache_name] += 1
    except KeyError:
        cache_counts[cache_name] = 1
    should_cache = cache_counts[cache_name] >= CACHE_LIMIT and cache_name not in cache_data

    archived_path = get_file_path(hex_string)
    is_zipped, name = index[hex_string]
    output:str|bytes
    if is_zipped and mode == "t":
        with open(archived_path, "rb") as f:
            output = gzip.decompress(f.read()).decode()
    elif is_zipped and mode == "b":
        with open(archived_path, "rb") as f:
            output = gzip.decompress(f.read())
    else:
        with open(archived_path, "r" + mode) as f:
            output = f.read()
    if should_cache:
        cache_data[cache_name] = output
    return output
