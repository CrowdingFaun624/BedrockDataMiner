import json
import subprocess
from typing import Iterator

from pathlib2 import Path

import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager
from Utilities.FunctionCaller import FunctionCaller, WaitValue


def read_cache() -> dict[str,dict[str,str]]:
    if not FileManager.FSB_CACHE_FILE.exists():
        with open(FileManager.FSB_CACHE_FILE, "wt") as f:
            json.dump({}, f)
    with open(FileManager.FSB_CACHE_FILE, "rt") as f:
        return json.load(f)

def write_cache(cache_data:dict[str,dict[str,str]]) -> None:
    with open(FileManager.FSB_CACHE_FILE, "wt") as f:
        json.dump(cache_data, f)

def cache_new_item(fsb_hash:str, data:dict[str,str]) -> None:
    cache = fsb_cache.get()
    cache[fsb_hash] = data
    write_cache(cache)

def cache_read_item(fsb_hash:str) -> dict[str,str]|None:
    '''Returns a dict of wav file names and file hashes in `./_assests/file_storage/objects` or None if the fsb file is unfamiliar.'''
    return fsb_cache.get().get(fsb_hash, None)

fsb_cache = WaitValue(read_cache)

def __output_file_all_done(input_file_releases:dict[str,bool], file_path:Path) -> None:
    input_file_releases[file_path.name] = True
    file_path.unlink()
    if all(input_file_releases.values()):
        Path(file_path.parent).rmdir()

def extract_fsb_file(input_file:FileManager.FilePromise|bytes) -> dict[str,FileManager.FilePromise]:

    if isinstance(input_file, FileManager.FilePromise):
        with input_file.open() as f:
            fsb_file_hash = FileManager.stringify_sha1_hash(FileManager.get_hash(f))
    else:
        fsb_file_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(input_file))
    cache_data = cache_read_item(fsb_file_hash)

    if cache_data is None:
        temp_directory = FileManager.get_temp_file_path()
        temp_directory.mkdir()
        temp_file = temp_directory.joinpath("fsb.fsb")
        # copying file to temp directory
        if isinstance(input_file, FileManager.FilePromise):
            with open(temp_file, "wb") as dest, input_file.open() as fsb_file_io:
                dest.write(fsb_file_io.read())
            input_file.all_done()
        else:
            with open(temp_file, "wb") as dest:
                dest.write(input_file)
        # run fsb extractor on fsb file.
        exe_return = subprocess.run([FileManager.LIB_FSB_EXE_FILE, temp_file], shell=True, cwd=temp_directory, capture_output=True)
        if exe_return.returncode != 0:
            raise Exceptions.SoundFilesExtractionError(input_file, exe_return.returncode)

        # look at what files are there.
        result_file_paths = [result_file for result_file in temp_directory.iterdir() if result_file.name != "fsb.fsb"]

        # hash files for cache
        result_file_hashes:dict[str,str] = {}
        for result_file_path in result_file_paths:
            with open(result_file_path, "rb") as f:
                result_file_hashes[result_file_path.name] = FileStorageManager.archive_data(f.read(), result_file_path.name)
        cache_new_item(fsb_file_hash, result_file_hashes)

        # return FilePromises
        temp_file.unlink()
        input_file_releases = {result_file_path.name: False for result_file_path in result_file_paths} # the all_done function will set its thing to True, and then delete the directory if all are True.
        return {
            result_file_path.name: FileManager.FilePromise(
                FunctionCaller(open, [result_file_path, "rb"]),
                ("%s %s" % (input_file.name, result_file_path.name) if isinstance(input_file, FileManager.FilePromise) else result_file_path.name),
                "b",
                FunctionCaller(__output_file_all_done, [input_file_releases, result_file_path])
            )
            for result_file_path in result_file_paths
        }

    else: # If the fsb has been seen before, then it returns its wav files from FileStorage
        if isinstance(input_file, FileManager.FilePromise):
            input_file.all_done()
        return {cached_file_path: FileStorageManager.open_archived(cached_file_hash, "b") for cached_file_path, cached_file_hash in cache_data.items()}

def extract_fsb_files(files:Iterator[tuple[str,FileManager.FilePromise|bytes]]) -> Iterator[tuple[str,dict[str,FileManager.FilePromise]]]:
    '''Adds all FilePromises to the queue. It yields the input FilePromise name and a dictionary of its result. Does not necessarily maintain the same order.'''
    for file_name, next_file in files:
        yield file_name, extract_fsb_file(next_file)
