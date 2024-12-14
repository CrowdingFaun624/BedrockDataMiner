import gzip
import shutil
import zipfile
from itertools import islice
from typing import Iterable, Literal

from pathlib2 import Path

import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.UserInput as UserInput
from Utilities.FunctionCaller import FunctionCaller

COMPRESSIBLE_FORMATS = [
    "lang",
    "json",
    "so", # code file
    "dex", # classes.dex
    "sf", # signature android manifest
    "mf", # android manifest
    "fsb",
    "exe"
]

ILLEGAL_FORMATS = ["jar"] # just in case a download site is sketchy lol

COMPRESS_SIZE = 65536 # size in bytes that it decides to make the file compressed

def version_exists(version_name:str) -> bool:
    '''Returns if the given version name is an existing index file.'''
    return version_name in get_version_list()

def get_version_list() -> list[str]:
    '''Returns all version names present in `./_assets/stored_versions/indexes.zip`.'''
    index_path = FileManager.STORED_VERSIONS_INDEXES_FILE
    index_zip = zipfile.ZipFile(index_path, "r")
    return [file.filename.replace(".txt", "") for file in index_zip.filelist]

def get_sizes(version_name:str) -> dict[str,int]:
    '''Returns a dictionary of file names to file sizes.'''
    index = read_index(version_name)
    sizes:dict[str,int] = {}
    for file_name, (hash, is_zipped) in index.items():
        path = get_hash_file_path(hash)
        file_size = path.stat().st_size
        sizes[file_name] = file_size
    sizes = reverse_dict(sort_dict_values(sizes))
    return sizes

def write_index(version_name:str, index:dict[str,tuple[str,bool]]) -> None:
    '''Writes the given hash index to the indexes archive.'''
    index_path = FileManager.STORED_VERSIONS_INDEXES_FILE
    index_zip = zipfile.ZipFile(index_path, "a")
    index_content = "\n".join("%s %i %s" % (file_properties[0], int(file_properties[1]), file_name) for file_name, file_properties in index.items())
    index_name = version_name + ".txt"
    if index_name in (file.filename for file in index_zip.filelist):
        print("Index \"%s\" already exists!" % version_name)
    else:
        index_zip.writestr(index_name, index_content, zipfile.ZIP_DEFLATED)

def read_index(version_name:str) -> dict[str,tuple[str,bool]]:
    '''Reads the given hash index file from the indexes archive.'''
    index_path = FileManager.STORED_VERSIONS_INDEXES_FILE
    index_zip = zipfile.ZipFile(index_path, "r")
    file_name = version_name + ".txt"
    if file_name not in (file.filename for file in index_zip.filelist):
        raise Exceptions.FileNotFoundInVersionArchive(file_name, version_name)
    index_content = index_zip.read(file_name).decode()
    index:dict[str,tuple[str,bool]] = {}
    for line in index_content.split("\n"):
        file_hash = line[:40]
        file_compressed = bool(int(line[41]))
        file_name = line[43:]
        index[file_name] = (file_hash, file_compressed)
    return index

def sort_dict(input_dict:dict) -> dict: # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    '''Returns a sorted copy of a dict by its keys.'''
    return {k: v for k, v in sorted(input_dict.items(), key=lambda item: item[0])}

def sort_dict_values(input_dict:dict) -> dict: # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    '''Returns a sorted copy of a dict by its values.'''
    return {k: v for k, v in sorted(input_dict.items(), key=lambda item: item[1])}

def reverse_dict(input_dict:dict) -> dict:
    '''Reverses the dictionary top-to-bottom-wise.'''
    return dict(reversed(input_dict.items()))

def extract(name:str, output_path:Path|None=None, index:dict[str,tuple[str,bool]]|None=None) -> None:
    '''Extracts an apk file from the archive into the given file name, or the output directory if not given.'''
    if output_path is None:
        output_path = FileManager.STORED_VERSIONS_OUTPUT_DIRECTORY.joinpath(name + ".apk")
    if index is None: index = read_index(name) # {filename: (hash, compressed)}
    if output_path.exists(): output_path.unlink()
    with zipfile.ZipFile(output_path, "w") as zip_file:
        for file_name, file_properties in index.items():
            file_hash, file_compressed = file_properties
            if file_compressed:
                with open(get_hash_file_path(file_hash), "rb") as f:
                    zip_file.writestr(file_name, gzip.decompress(f.read()), zipfile.ZIP_DEFLATED)
            else:
                zip_file.write(get_hash_file_path(file_hash), file_name, zipfile.ZIP_DEFLATED)

def extract_file(version_name:str, file_name:str, destination:Path, index:dict[str,tuple[str,bool]]|None=None) -> None:
    if index is None: index = read_index(version_name)
    if file_name not in index: raise Exceptions.FileNotFoundInVersionArchive(file_name, version_name)
    file_hash, file_compressed = index[file_name]
    for parent in reversed(destination.parents):
        parent:Path
        parent.mkdir(exist_ok=True)
    if file_compressed:
        with open(get_hash_file_path(file_hash), "rb") as f, open(destination, "wb") as g:
            g.write(gzip.decompress(f.read()))
    else:
        shutil.copy(get_hash_file_path(file_hash), destination)

def read_file(version_name:str, file_name:str, mode:str="b", index:dict[str,tuple[str,bool]]|None=None) -> bytes|str:
    if index is None: index = read_index(version_name)
    if file_name not in index: raise Exceptions.FileNotFoundInVersionArchive(file_name, version_name)
    file_hash, file_compressed = index[file_name]
    with open(get_hash_file_path(file_hash), "rb") as f:
        if file_compressed: data = gzip.decompress(f.read())
        else: data = f.read()
        if mode == "t":
            return data.decode("utf-8")
        else:
            return data

def get_file(version_name:str, file_name:str, mode:Literal["b", "t"]="b", index:dict[str,tuple[str,bool]]|None=None) -> FileManager.FilePromise:
    '''Returns a FilePromise of the object.'''
    if index is None: index = read_index(version_name)
    if file_name not in index: raise Exceptions.FileNotFoundInVersionArchive(file_name, version_name)
    file_hash, file_compressed = index[file_name]
    if file_compressed:
        temp_path = FileManager.get_temp_file_path()
        extract_file(version_name, file_name, temp_path, index)
        return FileManager.FilePromise(FunctionCaller(open, [temp_path, "r" + mode]), file_name.split("/")[-1], mode, temp_path.unlink)
    else:
        return FileManager.FilePromise(FunctionCaller(open, [get_hash_file_path(file_hash), "r" + mode]), file_name.split("/")[-1], mode)

def extract_files(version_name:str, files:Iterable[str], destinations:Iterable[Path]) -> None:
    '''Copies files from the given version to the given destinations.'''
    index = read_index(version_name)
    for file, destination in zip(files, destinations):
        extract_file(version_name, file, destination, index)

def archive_all() -> None:
    '''Archives the entire contents of the `./_assets/stored_versions/indexes` directory.'''
    for file in FileManager.STORED_VERSIONS_INPUT_DIRECTORY.iterdir():
        zip_file = open_zip_file(file)
        hashes = hash_files(zip_file)
        archive(file, hashes)
        print("archived \"%s\"." % file.name)

def archive(path:Path, hashes:dict[str,bytes], version_name:str|None=None) -> dict[str,tuple[str,bool]]:
    '''Places the contents of the zip file into the objects directory, and places an index file into the indexes directory.'''
    if version_name is None: version_name = path.stem
    zip_file = open_zip_file(path)
    index:dict[str,tuple[str,bool]] = {}
    objects_path = FileManager.STORED_VERSIONS_OBJECTS_DIRECTORY
    for zip_info in zip_file.infolist():
        if zip_info.is_dir():
            continue
        name = zip_info.filename
        if name.split(".")[-1].lower() in ILLEGAL_FORMATS:
            raise Exceptions.InvalidFileFormatError(name)
        file_hash = hashes[name]

        hex_hash = FileManager.stringify_sha1_hash(file_hash)
        zip_info.filename = str(get_hash_file_path(hex_hash, True)) # slightly evil code that makes it not spit thousands of directories everywhere
        str_hash = FileManager.stringify_sha1_hash(file_hash)
        new_path = get_hash_file_path(hex_hash)
        do_write = not new_path.exists()
        if do_write:
            zip_file.extract(zip_info, objects_path)
        compressed = name.split(".")[-1].lower() in COMPRESSIBLE_FORMATS and zip_info.file_size > COMPRESS_SIZE
        if compressed and do_write:
            with open(new_path, "rb") as f:
                data = gzip.compress(f.read())
            with open(new_path, "wb") as f:
                f.write(data)
        index[name] = (str_hash, compressed)
    index = sort_dict(index)
    write_index(version_name, index)
    return index

def hash_files(zip_file:zipfile.ZipFile) -> dict[str,bytes]:
    '''Takes in a ZipFile object, returns a dictionary of stored file names and their hashes.'''
    hashes:dict[str,bytes] = {}
    for file in zip_file.filelist:
        name = file.filename
        with zip_file.open(file) as file:
            hashes[name] = FileManager.get_hash(file)
    return hashes

def open_zip_file(path:Path) -> zipfile.ZipFile:
    '''Returns a ZipFile object in read mode from the given file name.'''
    zip_file = zipfile.ZipFile(path, "r")
    return zip_file

def get_hash_file_path(str_hash:str, return_string:bool=False) -> Path:
    '''Converts a string hash into a Path object.'''
    first_two = str_hash[:2]
    if return_string:
        return Path(first_two, str_hash)
    else:
        return FileManager.STORED_VERSIONS_OBJECTS_DIRECTORY.joinpath(first_two, str_hash)

def clear_objects() -> None:
    '''Clears all files and directories in the `./_assets/stored_versions/objects` directory. Requires user input.'''
    path = FileManager.STORED_VERSIONS_OBJECTS_DIRECTORY
    user_requirement = "I would like to remove all files from \"./_assets/stored_versions/objects\""
    print("Are you sure you want to remove all contents from `./_assets/stored_versions/objects`? (y/n) ")
    print("If so, type \"%s\"." % user_requirement)
    user_input = None
    while user_input != user_requirement:
        user_input = input()
    for file in path.iterdir():
        if file.is_dir():
            shutil.rmtree(file)
        else:
            file.unlink()
    print("Removed all files from `./_assets/stored_versions/objects`.")

def extract_user() -> None:
    '''Provides a user interface for extraction.'''
    file_list = get_version_list()
    user_input = UserInput.input_single({file: file for file in file_list}, "file", show_options_first_time=True, close_enough=True)
    extract(user_input)
    print("Extracted \"%s\"" % user_input)

def stats_user() -> None:
    file_list = get_version_list()
    user_input = UserInput.input_single({file: file for file in file_list}, "file", show_options_first_time=True, close_enough=True)
    sizes = get_sizes(user_input)
    top_sizes = dict(islice(sizes.items(), 50))
    print("Top sizes from \"%s\":" % user_input)
    print("\t" + "".join("\n\t%s: %i" % (file_name, file_size) for file_name, file_size in top_sizes.items()))

def main() -> None:
    PROGRAMS = {
        "archive": archive_all,
        "clear_all": clear_objects,
        "extract": extract_user,
        "stats": stats_user,
    }
    UserInput.input_single(PROGRAMS, "program", show_options=True, close_enough=True)()
