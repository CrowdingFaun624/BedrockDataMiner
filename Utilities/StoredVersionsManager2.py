import gzip
from pathlib2 import Path
import threading
from typing import Literal, TypedDict
import zipfile

import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller

COMPRESSIBLE_FILES = ["json", "fsb", "nbt", "txt", "lang", "tga", "xml", "bin", "fragment", "h", "vertex", "properties", "material", "ttf", "otf", "fontdata", "mcstructure", "css", "js", "html", "dat", "wlist", "pdn", "so", "dex", "sf", "mf", "kotlin_builtins", "mp3", "arsc", "mf", "sf"]

class IndexTypedDict(TypedDict):
    sha1: str
    z: int

def reopen_in_binary(file:FileManager.FilePromise) -> FileManager.FilePromise:
    '''Returns a new FilePromise in binary mode if the current one is in text mode.'''
    if file.mode == "t":
        temp_file_path = FileManager.get_temp_file_path()
        with open(temp_file_path, "wt") as temp_file, file.open() as file_io:
            temp_file.write(file_io.read())
        file.all_done()
        return FileManager.FilePromise(FunctionCaller(open, [temp_file_path, "rb"]), file.name, "b", temp_file_path.unlink)
    else: return file

def should_zip_file(file:FileManager.FilePromise) -> bool:
    '''Returns if the file is efficiently zippable.'''
    file_name = file.name.split("/")[-1].split("\\")[-1]
    file_suffix = file_name.split(".")[-1].lower() if "." in file_name else ""
    return file_suffix in COMPRESSIBLE_FILES

def get_file_path(hex_string:str) -> Path:
    archived_folder = Path(FileManager.STORED_VERSIONS2_OBJECTS_FOLDER.joinpath(hex_string[:2]))
    archived_folder.mkdir(exist_ok=True)
    archived_path = Path(archived_folder.joinpath(hex_string))
    return archived_path

def archive(file:FileManager.FilePromise) -> tuple[str,bool]:
    '''Takes in a FilePromise object, and stores a file in the `./_assets/stored_versions/objects` directory, and returns its sha1 hash as a hexadecimal string and whether it was zipped.
    If the file already exists in the archive, it returns the hash and if it's already zipped.
    Will always call all_done on the file.'''
    file = reopen_in_binary(file)
    hash_bytes = FileManager.get_hash(file.open())
    hash_string = FileManager.stringify_sha1_hash(hash_bytes)
    destination_path = get_file_path(hash_string)
    if destination_path.exists() and hash_string in zippedness_index:
        return hash_string, zippedness_index[hash_string]
    is_zipped = should_zip_file(file)
    with open(destination_path, "wb") as destination, file.open() as source:
        if FileManager.get_file_size(source) == 0:
            raise ValueError("File \"%s\" returned an IO object with length 0!" % file.name)
        if is_zipped:
            destination.write(gzip.compress(source.read()))
        else:
            destination.write(source.read())
    file.all_done()

    write_zippedness_index(hash_string, is_zipped)
    return hash_string, is_zipped

def get_file(hash:str, is_zipped:bool, mode:Literal["b", "t"]="b") -> FileManager.FilePromise:
    path = get_file_path(hash)
    match is_zipped, mode:
        case False, "b":
            return FileManager.FilePromise(FunctionCaller(open, [path, "rb"]), hash, "b")
        case True, "b":
            temp_path = FileManager.get_temp_file_path()
            with open(path, "rb") as file_io, open(temp_path, "wb") as temp_io:
                temp_io.write(gzip.decompress(file_io.read()))
            return FileManager.FilePromise(FunctionCaller(open, [temp_path, "rb"]), hash, "b", temp_path.unlink)
        case False, "t":
            return FileManager.FilePromise(FunctionCaller(open, [path, "rt"]), hash, "t")
        case True, "t":
            temp_path = FileManager.get_temp_file_path()
            with open(path, "rb") as file_io, open(temp_path, "wb") as temp_io:
                temp_io.write(gzip.decompress(file_io.read()))
            return FileManager.FilePromise(FunctionCaller(open, [temp_path, "rt"]), hash, "t", temp_path.unlink)
        case _:
            raise ValueError("Illegal arguments \"%s\" and/or \"%s\"!" % (is_zipped, mode))

def read(hash:str, is_zipped:bool, mode:Literal["b", "t"]="b") -> str|bytes:
    path = get_file_path(hash)
    match is_zipped, mode:
        case False, "b":
            with open(path, "rb") as file_io:
                return file_io.read()
        case True, "b":
            with open(path, "rb") as file_io:
                return gzip.decompress(file_io.read())
        case False, "t":
            with open(path, "rt") as file_io:
                return file_io.read()
        case True, "t":
            with open(path, "rb") as file_io:
                return gzip.decompress(file_io.read()).decode()
        case _:
            raise ValueError("Illegal arguments \"%s\" and/or \"%s\"!" % (is_zipped, mode))

def extract(index:dict[str,IndexTypedDict], destination:Path) -> None:
    if destination.exists(): destination.unlink()
    with zipfile.ZipFile(destination, "w") as zip_file:
        for file_name, file_properties in index.items():
            hash_string = file_properties["sha1"]
            is_zipped = bool(file_properties["z"])
            zip_file.writestr(file_name, read(hash_string, is_zipped, "b"), zipfile.ZIP_DEFLATED)

def read_zippedness_index() -> dict[str,bool]:
    with open(FileManager.STORED_VERSIONS2_INDEX_FILE, "rt") as index_file_io, index_lock:
        index_lines = index_file_io.readlines()
    return {line[:40]: bool(int(line[41])) for line in index_lines}

def write_zippedness_index(hash:str, zipped:bool) -> None:
    '''Appends a line to the zippedness index file and memory object.'''
    if not isinstance(hash, str):
        raise TypeError("`hash` is not a str!")
    if len(hash) != 40:
        raise ValueError("`hash` is not length 40!")
    if not isinstance(zipped, bool):
        raise TypeError("`zipped` is not a bool!")
    with open(FileManager.STORED_VERSIONS2_INDEX_FILE, "at") as index_file_io, index_lock:
        index_file_io.write("%s %i\n" % (hash, zipped))
        zippedness_index[hash] = zipped

def get_size(hash:str) -> int:
    '''Gets the size of the compressed file.'''
    file = get_file(hash, False, "b")
    with file.open() as file_io:
        output = FileManager.get_file_size(file_io)
    file.all_done()
    return output

def get_total_size() -> int:
    '''Returns the size of the objects folder's contents in bytes.'''
    total_size = 0
    for folder in FileManager.STORED_VERSIONS2_OBJECTS_FOLDER.iterdir():
        for file in folder.iterdir():
            with open(file, "rb") as f:
                total_size += FileManager.get_file_size(f)
    return total_size

index_lock = threading.Lock()
zippedness_index = read_zippedness_index()
