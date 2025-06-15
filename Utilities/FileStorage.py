import datetime
import gzip
import shutil
import zipfile
from itertools import islice
from pathlib import Path
from typing import Callable, Iterable, overload

from send2trash import send2trash

import Domain.Domain as Domain
from Downloader.DirectoryAccessor import DirectoryAccessor
from Utilities.Cache import LinesCache
from Utilities.FileManager import (
    FILE_STORAGE_INDEX_FILE,
    FILE_STORAGE_OBJECTS_DIRECTORY,
    OUTPUT_DIRECTORY,
    get_hash_hexdigest,
    get_temp_file_path,
)
from Utilities.UserInput import input_single

COMPRESSIBLE_FILES = {"json", "fsb", "txt", "lang", "tga", "xml", "bin", "fragment", "h", "vertex", "properties", "material", "ttf", "otf", "fontdata", "css", "js", "html", "dat", "wlist", "pdn", "so", "dex", "sf", "mf"}

class FileStorageIndex(LinesCache[dict[str,bool], tuple[str,bool]]):
    '''
    Cache of a dictionary of hex strings to zippability.
    '''

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(FILE_STORAGE_INDEX_FILE)

    def get_default_content(self) -> dict[str, bool] | None:
        return {}

    def deserialize(self, data: bytes) -> dict[str, bool]:
        return {line[:40]: bool(int(line[41])) for line in data.decode("UTF8").splitlines()}

    def serialize(self, data: dict[str, bool]) -> bytes:
        return ("\n".join(f"{key} {int(value)}" for key, value in index.get().items()) + "\n").encode("UTF8")

    def serialize_line(self, data: tuple[str, bool]) -> str:
        return f"{data[0]} {int(data[1])}\n"

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
    archived_directory = FILE_STORAGE_OBJECTS_DIRECTORY.joinpath(hex_string[:2])
    archived_path = archived_directory.joinpath(hex_string)
    return archived_path

@overload
def is_archived(*, data:bytes) -> bool: ...
@overload
def is_archived(*, file_hash:str) -> bool: ...
def is_archived(*, data:bytes|None=None, file_hash:str|None=None) -> bool:
    if file_hash is None:
        assert data is not None
        file_hash = get_hash_hexdigest(data)
    return get_file_path(file_hash).exists()

def archive_data(data:bytes, file_name:str) -> str:
    '''Takes in bytes, and stores a file in the `./_assets/file_storage/objects` directory, and adds its data to the `./_assets/file_storage/index.txt` file.
    Returns the sha1 hash in a hexadecimal string format that the file is stored at.
    If the file already exists in the archive, do nothing.'''
    file_hash = get_hash_hexdigest(data)
    archived_directory = FILE_STORAGE_OBJECTS_DIRECTORY.joinpath(file_hash[:2])
    archived_path = get_file_path(file_hash)
    if archived_path.exists():
        return file_hash
    archived_directory.mkdir(exist_ok=True)
    zipped = should_zip_file(file_name)
    with open(archived_path, "wb") as destination:
        if zipped:
            destination.write(gzip.compress(data))
        else:
            destination.write(data)

    try:
        if file_hash not in index.get():
            index.write_new_line((file_hash, zipped))
    except:
        # if the index is not written to, then the file system is considered corrupted.
        archived_path.unlink()
        raise

    return file_hash

def read_archived(hex_string:str) -> bytes:
    with open(get_file_path(hex_string), "rb") as f:
        if index.get()[hex_string]:
            return gzip.decompress(f.read())
        else:
            return f.read()

def recycle_items(hex_strings:Iterable[str]) -> None:
    temp_directory = get_temp_file_path()
    temp_directory.mkdir()
    objects_directory = temp_directory.joinpath("objects")
    objects_directory.mkdir()
    trash_index:list[str] = []
    for hex_string in hex_strings:
        index_item = index.get().pop(hex_string, None)
        if index_item is not None:
            trash_index.append(index.serialize_line((hex_string, index_item)))
        source_path = get_file_path(hex_string)
        if source_path.exists():
            destination_path = objects_directory.joinpath(source_path.name)
            shutil.move(source_path, destination_path)
            print(f"Recycled {hex_string}")
        else:
            print(f"{source_path} was not present.")
    with open(temp_directory.joinpath("index.txt"), "wt") as f:
        f.write("".join(trash_index))
    output_recycle_directory = OUTPUT_DIRECTORY.joinpath(f"recycled-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}")
    shutil.move(temp_directory, output_recycle_directory)
    send2trash(output_recycle_directory)
    index.write()

def recycle_items_main(domain:"Domain.Domain") -> None:
    files_str = input("Choose multiple space-delimited hexadecimal names: ")
    user_files = files_str.split(" ")
    files:list[str] = []
    for user_file in user_files:
        if len(user_file) != 40 or not all(char.isalnum() for char in user_file):
            print(f"Invalid file \"{user_file}\"")
            continue
        files.append(user_file)
    recycle_items(files)

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

def create_archive(domain:"Domain.Domain") -> None:
    while not any(file.suffix.lower() == ".zip" for file in OUTPUT_DIRECTORY.iterdir()):
        input("Place a zip file in the \"_output\" directory. (Press enter to continue)")
    file:Path|None = None
    for file in OUTPUT_DIRECTORY.iterdir():
        if file.suffix.lower() == ".zip":
            break
    assert file is not None
    zip_file = zipfile.ZipFile(file, "r")
    index:dict[str,tuple[str,bool]] = {}
    for zip_info in zip_file.infolist():
        if zip_info.is_dir():
            continue
        file_contents = zip_file.read(zip_info)
        file_hash = get_hash_hexdigest(file_contents)
        archive_data(file_contents, zip_info.filename)
        index[zip_info.filename] = (file_hash, should_zip_file(zip_info.filename))
    index = {key: value for key, value in sorted(index.items(), key=lambda item: item[0])}
    archive_path = OUTPUT_DIRECTORY.joinpath(file.name + "_archived.txt")
    with open(archive_path, "wt") as f:
        f.write("\n".join(f"{file_hash} {int(is_zipped)} {file_name}" for file_name, (file_hash, is_zipped) in index.items()))
    print(f"Archived version. Index is at \"{archive_path.name}\".")

def version_summary(domain:"Domain.Domain") -> None:
    version = input_single(domain.versions, "version")
    version_file_type = input_single(version.version_files_dict, "version file type", show_options=True, close_enough=True)
    files = version_file_type.get_accessor(DirectoryAccessor).file_list
    file_extensions:dict[str,int] = {}
    for file in files:
        file_name = file.split("/")[-1]
        if "." in file_name:
            file_extension = file_name.split(".")[-1]
        else:
            file_extension = ""
        if file_extension in file_extensions:
            file_extensions[file_extension] += 1
        else:
            file_extensions[file_extension] = 1
    sorted_file_extensions = {extension: count for count, extension in sorted([(count, extension) for extension, count in file_extensions.items()], reverse=True)}
    print(f"There are {len(files)} files overall in {version.name}.")
    for extension, count in sorted_file_extensions.items():
        print(f"There are {count} files with the \"{extension}\" extension.")

def get_file(domain:"Domain.Domain") -> None:
    version = input_single(domain.versions, "version")
    file = input("File: ")
    version_file_type = input_single(version.version_files_dict, "version file type", show_options=True, close_enough=True)
    install_accessor = version_file_type.get_accessor(DirectoryAccessor)
    if install_accessor is not None:
        destination = version.version_directory.joinpath(file)
        file_data = install_accessor.read(file)
        with open(destination, "wb") as destination_file:
            destination_file.write(file_data)
        print(f"File is in {destination}")
    else:
        print(f"Version \"{version.name}\" is not archived.")

def stats(domain:"Domain.Domain") -> None:
    sizes = {file.name: file.stat().st_size for directory in FILE_STORAGE_OBJECTS_DIRECTORY.iterdir() for file in directory.iterdir()}
    sizes = dict((name, size) for name, size in sorted(sizes.items(), key=lambda item: item[1], reverse=True))
    top_sizes = dict(islice(sizes.items(), 50))
    print("Top sizes:")
    print(f"\t{"".join(f"\n\t{file_name}: {file_size}" for file_name, file_size in top_sizes.items())}")

def main(domain:"Domain.Domain") -> None:
    PROGRAMS:dict[str,Callable[[Domain.Domain],None]] = {
        "create_archive": create_archive,
        "get_file": get_file,
        "recycle_items": recycle_items_main,
        "stats": stats,
        "version_summary": version_summary,
    }
    input_single(PROGRAMS, "program", show_options=True, close_enough=True)(domain)
