import gzip
from typing import IO, Literal, overload

from pathlib2 import Path

import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller, WaitValue

COMPRESSIBLE_FILES = ["json", "fsb", "txt", "lang", "tga", "xml", "bin", "fragment", "h", "vertex", "properties", "material", "ttf", "otf", "fontdata", "css", "js", "html", "dat", "wlist", "pdn", "so", "dex", "sf", "mf"]

def read_index() -> dict[str, bool]:
    '''Returns a dictionary of hex string hashes, and the file's zippability and a name it has.
    Should only be called once at the start of the program, and then the `index` variable should be used.'''
    with open(FileManager.FILE_STORAGE_INDEX_FILE, "rt") as index_file_io:
        return {line[:40]: bool(int(line[41])) for line in index_file_io.readlines()}

index = WaitValue(read_index)

def should_zip_file(file_path:str) -> bool:
    '''Returns if the file is efficiently zippable.'''
    file_name = file_path.split("/")[-1].split("\\")[-1]
    file_end = file_name.split(".")[-1].lower() if "." in file_name else ""
    return file_end in COMPRESSIBLE_FILES

def get_file_path(hex_string:str) -> Path:
    archived_directory = FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.joinpath(hex_string[:2])
    archived_path = archived_directory.joinpath(hex_string)
    return archived_path

def archive_data(data:bytes, file_name:str, *, empty_okay:bool=False) -> str:
    '''Takes in bytes, and stores a file in the `./_assets/file_storage/objects` directory, and adds its data to the `./_assets/file_storage/index.txt` file.
    Returns the sha1 hash in a hexadecimal string format that the file is stored at.
    If the file already exists in the archive, do nothing.'''
    file_hash = FileManager.get_hash_bytes(data)
    hex_string = FileManager.stringify_sha1_hash(file_hash)
    archived_directory = FileManager.FILE_STORAGE_OBJECTS_DIRECTORY.joinpath(hex_string[:2])
    archived_path = get_file_path(hex_string)
    if archived_path.exists():
        return hex_string
    archived_directory.mkdir(exist_ok=True)
    zipped = should_zip_file(file_name)
    with open(archived_path, "wb") as destination:
        if not empty_okay and len(data) == 0:
            raise Exceptions.EmptyFileError(message="(hash %s)" % (hex_string,))
        if zipped:
            destination.write(gzip.compress(data))
        else:
            destination.write(data)

    if hex_string not in index.get():
        with open(FileManager.FILE_STORAGE_INDEX_FILE, "at") as index_file:
            index_file.write("%s %i\n" % (hex_string, zipped))
        index.get()[hex_string] = zipped

    return hex_string

def open_archived(hex_string:str, mode:Literal["t", "b"]) -> FileManager.FilePromise:
    archived_path = get_file_path(hex_string)
    if not archived_path.exists():
        raise Exceptions.FileHashNotFound(hex_string)
    is_zipped = index.get()[hex_string]
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
    archived_path = get_file_path(hex_string)
    is_zipped = index.get()[hex_string]
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
    return output

def delete_item(hex_string:str) -> None:
    '''
    Deletes the item from the index and objects.
    Must save the index for changes to be saved.
    '''
    del index.get()[hex_string]
    path = get_file_path(hex_string)
    path.unlink()

def remove_index_values_without_associated_file() -> None:
    '''
    Removes all index entries such that there is no file
    stored at that hash. Saves automatically.
    '''
    loaded_index = index.get()
    items_to_delete:list[str] = []
    for key in loaded_index.keys():
        if not get_file_path(key).exists():
            items_to_delete.append(key)
    for item in items_to_delete:
        del loaded_index[item]
    save_index()

def save_index() -> None:
    '''
    Saves the index.
    Is only necessary when an item is deleted from the index.
    '''
    with open(FileManager.FILE_STORAGE_INDEX_FILE, "wt") as index_file:
        index_file.write("\n".join("%s %i" % (key, value) for key, value in index.get().items()) + "\n")
