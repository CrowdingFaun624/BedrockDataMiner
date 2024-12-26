import gzip
from pathlib import Path

import Utilities.Cache as Cache
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager

COMPRESSIBLE_FILES = ["json", "fsb", "txt", "lang", "tga", "xml", "bin", "fragment", "h", "vertex", "properties", "material", "ttf", "otf", "fontdata", "css", "js", "html", "dat", "wlist", "pdn", "so", "dex", "sf", "mf"]

class FileStorageIndex(Cache.LinesCache[dict[str,bool], tuple[str,bool]]):
    '''
    Cache of a dictionary of hex strings to zippability.
    '''
    
    def __init__(self) -> None:
        super().__init__(FileManager.FILE_STORAGE_INDEX_FILE)
    
    def get_default_content(self) -> dict[str, bool] | None:
        return {}
    
    def deserialize(self, data: bytes) -> dict[str, bool]:
        return {line[:40]: bool(int(line[41])) for line in data.decode("UTF8").splitlines()}

    def serialize(self, data: dict[str, bool]) -> bytes:
        return ("\n".join("%s %i" % (key, value) for key, value in index.get().items()) + "\n").encode("UTF8")

    def serialize_line(self, data: tuple[str, bool]) -> str:
        return "%s %i\n" % data

    def append_new_line(self, data: tuple[str, bool]) -> None:
        key, value = data
        self.get()[key] = value

index = FileStorageIndex()

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
        index.write_new_line((hex_string, zipped))

    return hex_string

def read_archived(hex_string:str) -> bytes:
    with open(get_file_path(hex_string), "rb") as f:
        if index.get()[hex_string]:
            return gzip.decompress(f.read())
        else:
            return f.read()

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
    index.write()
