import subprocess
from typing import Iterator

import Utilities.Cache as Cache
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager


class FsbCache(Cache.JsonCache[dict[str,dict[str,str]]]):

    def __init__(self) -> None:
        super().__init__(FileManager.FSB_CACHE_FILE)

    def get_default_content(self) -> dict[str, str] | None:
        return {}

    def new_item(self, fsb_hash:str, data:dict[str,str]) -> None:
        self.get()[fsb_hash] = data
        self.write()

fsb_cache = FsbCache()

def extract_fsb_file(input_file:bytes) -> Iterator[tuple[str,bytes]]:
    fsb_file_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(input_file))
    cache_data = fsb_cache.get().get(fsb_file_hash)
    if cache_data is not None:
        yield from ((cached_file_path, FileStorageManager.read_archived(cached_file_hash)) for cached_file_path, cached_file_hash in cache_data.items())
        return

    temp_directory = FileManager.get_temp_file_path()
    temp_directory.mkdir()
    temp_file = temp_directory.joinpath("fsb.fsb")
    # copying file to temp directory
    with open(temp_file, "wb") as dest:
        dest.write(input_file)
    # run fsb extractor on fsb file.
    exe_return = subprocess.run([FileManager.LIB_FSB_EXE_FILE, temp_file], shell=True, cwd=temp_directory, capture_output=True)
    if exe_return.returncode != 0:
        raise Exceptions.SoundFilesExtractionError(exe_return.returncode)

    # look at what files are there.
    result_file_paths = [result_file for result_file in temp_directory.iterdir() if result_file.name != "fsb.fsb"]

    # hash files for cache and yield output
    result_file_hashes:dict[str,str] = {}
    for result_file_path in result_file_paths:
        with open(result_file_path, "rb") as f:
            contents = f.read()
            result_file_hashes[result_file_path.name] = FileStorageManager.archive_data(contents, result_file_path.name)
            yield result_file_path.name, contents
    fsb_cache.new_item(fsb_file_hash, result_file_hashes)

    # clean up
    temp_file.unlink()
    for result_file_path in result_file_paths:
        result_file_path.unlink()
    temp_directory.rmdir()
