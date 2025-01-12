import subprocess
from typing import Iterator, Optional

import Domain.Domain as Domain
import Domain.Domains as Domains
import Utilities.Cache as Cache
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.FileStorage as FileStorage


class SoundFilesExtractionError(Exceptions.DataminerException):
    "Failure to extract from an FSB file."

    def __init__(self, exit_code:int, message:Optional[str]=None) -> None:
        '''
        :exit_code: The exit code that the extraction executable returned.
        :message: Additional text to place after the main message.
        '''
        super().__init__(exit_code, message)
        self.exit_code = exit_code
        self.message = message

    def __str__(self) -> str:
        return f"Failed to extract FSB file; returned exit code {self.exit_code}{Exceptions.message(self.message)}"

class FsbCache(Cache.JsonCache[dict[str,dict[str,str]]]):

    def __init__(self, domain:"Domain.Domain") -> None:
        domain.data_directory.mkdir(exist_ok=True)
        super().__init__(domain.data_directory.joinpath("fsb_cache.json"))

    def get_default_content(self) -> dict[str, str] | None:
        return {}

    def new_item(self, fsb_hash:str, data:dict[str,str]) -> None:
        self.get()[fsb_hash] = data
        self.write()

fsb_cache = FsbCache(Domains.get_domain_from_module(__name__))

def extract_fsb_file(input_file:bytes) -> Iterator[tuple[str,bytes]]:
    domain = Domains.get_domain_from_module(__name__)
    fsb_file_hash = FileManager.get_hash_hexdigest(input_file)
    cache_data = fsb_cache.get().get(fsb_file_hash)
    if cache_data is not None:
        yield from ((cached_file_path, FileStorage.read_archived(cached_file_hash)) for cached_file_path, cached_file_hash in cache_data.items())
        return

    temp_directory = FileManager.get_temp_file_path()
    temp_directory.mkdir()
    temp_file = temp_directory.joinpath("fsb.fsb")
    # copying file to temp directory
    with open(temp_file, "wb") as dest:
        dest.write(input_file)
    # run fsb extractor on fsb file.
    exe_return = subprocess.run([domain.lib_files["fsb/fsb_aud_extr.exe"], temp_file], shell=True, cwd=temp_directory, capture_output=True)
    if exe_return.returncode != 0:
        raise SoundFilesExtractionError(exe_return.returncode)

    # look at what files are there.
    result_file_paths = [result_file for result_file in temp_directory.iterdir() if result_file.name != "fsb.fsb"]

    # hash files for cache and yield output
    result_file_hashes:dict[str,str] = {}
    for result_file_path in result_file_paths:
        with open(result_file_path, "rb") as f:
            contents = f.read()
            result_file_hashes[result_file_path.name] = FileStorage.archive_data(contents, result_file_path.name)
            yield result_file_path.name, contents
    fsb_cache.new_item(fsb_file_hash, result_file_hashes)

    # clean up
    temp_file.unlink()
    for result_file_path in result_file_paths:
        result_file_path.unlink()
    temp_directory.rmdir()
