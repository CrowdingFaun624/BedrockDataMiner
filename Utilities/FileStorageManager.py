import gzip
from pathlib2 import Path
import threading
from typing import IO, Literal

import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller

COMPRESSIBLE_FILES = ["json", "fsb", "nbt", "txt", "lang", "tga", "xml", "bin", "fragment", "h", "vertex", "properties", "material", "ttf", "otf", "fontdata", "mcstructure", "css", "js", "html", "dat", "wlist", "pdn", "so", "dex", "sf", "mf"]

index_lock = threading.Lock()

def read_index() -> dict[str, tuple[bool, str]]:
    '''Returns a dictionary of hex string hashes, and the file's zippability and a name it has.
    Should only be called once at the start of the program, and then the `index` variable should be used.'''
    index_lock.acquire()
    with open(FileManager.FILE_STORAGE_INDEX_FILE, "rt") as index_file_io:
        index_lines = index_file_io.readlines()
    index_lock.release()
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
    archived_folder = Path(FileManager.FILE_STORAGE_OBJECTS_FOLDER.joinpath(hex_string[:2]))
    archived_path = Path(archived_folder.joinpath(hex_string))
    return archived_path

def archive(file:FileManager.FilePromise) -> str:
    '''Takes in a FilePromise object, and stores a file in the `./_assets/file_storage/objects` directory, and adds its data to the `./_assets/file_storage/index.txt` file.
    Returns the sha1 hash in a hexadecimal string format that the file is stored at.
    If the file already exists in the archive, do nothing.'''
    file = reopen_in_binary(file)
    file_hash = FileManager.get_hash(file.open())
    hex_string = FileManager.stringify_sha1_hash(file_hash)
    archived_folder = Path(FileManager.FILE_STORAGE_OBJECTS_FOLDER.joinpath(hex_string[:2]))
    archived_path = get_file_path(hex_string)
    archived_folder.mkdir(exist_ok=True)
    zipped = should_zip_file(file)
    with open(archived_path, "wb") as destination, file.open() as source:
        if FileManager.get_file_size(source) == 0:
            raise ValueError("File \"%s\" returned an IO object with length 0!" % file.name)
        if zipped:
            destination.write(gzip.compress(source.read()))
        else:
            destination.write(source.read())

    index_lock.acquire()
    with open(FileManager.FILE_STORAGE_INDEX_FILE, "at") as index_file:
        index_file.write("%s %i %s\n" % (hex_string, zipped, file.name))
    index[hex_string] = (zipped, file.name)
    index_lock.release()

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
            temp_file_io.write(gzip.decompress(f))
        return FileManager.FilePromise(FunctionCaller(open, [temp_file, "r" + mode]), temp_file.name, "b", temp_file.unlink)
    else:
        return FileManager.FilePromise(FunctionCaller(open, [archived_path, "r" + mode]), hex_string, "b")

def read_archived(hex_string:str, mode:Literal["t", "b"]) -> bytes|str:
    archived_path = get_file_path(hex_string)
    is_zipped, name = index[hex_string]
    if is_zipped and mode == "t":
        with open(archived_path, "rb") as f:
            return gzip.decompress(f).decode()
    elif is_zipped and mode == "b":
        with open(archived_path, "rb") as f:
            return gzip.decompress(f)
    else:
        with open(archived_path, "r" + mode) as f:
            return f.read()
