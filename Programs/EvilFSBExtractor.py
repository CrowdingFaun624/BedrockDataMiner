import json
from pathlib2 import Path
import subprocess
import threading
from typing import Generator, Iterable

import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager
from Utilities.FunctionCaller import FunctionCaller, WaitValue

fsb_exe_lock = threading.Lock()
cache_file_lock = threading.Lock()

def read_cache() -> dict[str,dict[str,str]]:
    if not FileManager.FSB_CACHE_FILE.exists():
        with open(FileManager.FSB_CACHE_FILE, "wt") as f, cache_file_lock:
            json.dump({}, f)
    with open(FileManager.FSB_CACHE_FILE, "rt") as f, cache_file_lock:
        return json.load(f)

def write_cache(cache_data:dict[str,dict[str,str]]) -> None:
    with open(FileManager.FSB_CACHE_FILE, "wt") as f, cache_file_lock:
        json.dump(cache_data, f)

def cache_new_item(fsb_hash:str, data:dict[str,str]) -> None:
    if not isinstance(fsb_hash, str):
        raise TypeError("`fsb_hash` is not a str!")
    if len(fsb_hash) != 40:
        raise ValueError("`fsb_hash` is len %i instead of 40: \"%s\"!" % (len(fsb_hash), fsb_hash))
    if not isinstance(data, dict):
        raise TypeError("`data` is not a dict!")
    for key, value in data.items():
        if not isinstance(key, str): 
            raise TypeError("A key in `data` is not a str: \"%s\"" % key)
        if not isinstance(value, str):
            raise TypeError("A value in `data` is not a str: \"%s\": \"%s\"!" % (key, value))
        if len(value) != 40:
            raise ValueError("A value in `data` is len %i isntead of 40: \"%s\": \"%s\"!" % (len(value), key, value))
    
    cache = fsb_cache.get()
    with cache_file_lock:
        cache[fsb_hash] = data
    write_cache(cache)

def cache_read_item(fsb_hash:str) -> dict[str,str]|None:
    '''Returns a dict of wav file names and file hashes in `./_assests/file_storage/objects` or None if the fsb file is unfamiliar.'''
    cache = fsb_cache.get()
    if fsb_hash in cache:
        return cache[fsb_hash]
    else:
        return None

fsb_cache = WaitValue(FunctionCaller(read_cache))

def __output_file_all_done(input_file_releases:dict[str,bool], file_path:Path) -> None:
    file_name = file_path.name
    if file_name not in input_file_releases:
        raise KeyError("\"%s\" is not a key in %s!" % (file_name, input_file_releases))
    input_file_releases[file_name] = True
    file_path.unlink()
    if all(input_file_releases.values()):
        file_path.parent.rmdir()

def extract_fsb_file(input_file:FileManager.FilePromise) -> dict[str,FileManager.FilePromise]:

    with input_file.open() as f:
        fsb_file_hash = FileManager.stringify_sha1_hash(FileManager.get_hash(f))
    cache_data = cache_read_item(fsb_file_hash)
    
    if cache_data is None:
        temp_directory = FileManager.get_temp_file_path()
        temp_directory.mkdir()
        temp_file = Path(temp_directory.joinpath("fsb.fsb"))
        # copying file to temp directory
        with open(temp_file, "wb") as dest, input_file.open() as fsb_file_io:
            dest.write(fsb_file_io.read())
        input_file.all_done()
        # run fsb extractor on fsb file.
        with fsb_exe_lock as lock: # They raise an error code of 67 if started at exactly the same time.
            exe_return = subprocess.run([FileManager.LIB_FSB_EXE_FILE, temp_file], shell=True, cwd=temp_directory, capture_output=True)
        if exe_return.returncode != 0:
            raise RuntimeError("EvilFSBExtractor returned a code of %i on file \"%s\"!" % (exe_return.returncode, input_file.name))

        # look at what files are there.
        result_file_paths = [result_file for result_file in temp_directory.iterdir() if result_file.name != "fsb.fsb"]

        # hash files for cache
        result_file_hashes:dict[str,str] = {}
        for result_file_path in result_file_paths:
            with open(result_file_path, "rb") as f:
                result_file_hashes[result_file_path.name] = FileStorageManager.archive_io(f, result_file_path.name)
        cache_new_item(fsb_file_hash, result_file_hashes)

        # return FilePromises
        temp_file.unlink()
        input_file_releases = {result_file_path.name: False for result_file_path in result_file_paths} # the all_done function will set its thing to True, and then delete the folder if all are True.
        return {result_file_path.name: FileManager.FilePromise(FunctionCaller(open, [result_file_path, "rb"]), "%s %s" % (input_file.name, result_file_path.name), "b", FunctionCaller(__output_file_all_done, [input_file_releases, result_file_path])) for result_file_path in result_file_paths}
    
    else: # If the fsb has been seen before, then it returns its wav files from FileStorage
        input_file.all_done()
        return {cached_file_path: FileStorageManager.open_archived(cached_file_hash, "b") for cached_file_path, cached_file_hash in cache_data.items()}

def extract_fsb_files(files:Iterable[tuple[str,FileManager.FilePromise]]|Generator[tuple[str,FileManager.FilePromise],None,None]) -> Generator[tuple[str,dict[str,FileManager.FilePromise]],None,None]:
    '''Adds all FilePromises to the queue. It yields the input FilePromise name and a dictionary of its result. Does not necessarily maintain the same order.'''
    if not isinstance(files, Iterable):
        raise TypeError("`files` is not an Iterable!")
    for file_name, next_file in files:
        if not isinstance(next_file, FileManager.FilePromise):
            raise TypeError("`files` has an item that is not a FilePromise!")
        yield file_name, extract_fsb_file(next_file)
