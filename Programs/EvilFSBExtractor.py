from pathlib2 import Path
import subprocess
from typing import Generator, Iterable

import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import FunctionCaller

def __output_file_all_done(input_file_releases:dict[str,bool], file_path:Path) -> dict[str,FileManager.FilePromise]:
    file_name = file_path.name
    if file_name not in input_file_releases:
        raise KeyError("\"%s\" is not a key in %s!" % (file_name, input_file_releases))
    input_file_releases[file_name] = True
    file_path.unlink()
    if all(input_file_releases.values()):
        file_path.parent.rmdir()

def extract_fsb_file(input_file:FileManager.FilePromise) -> None:
    temp_directory = FileManager.get_temp_file_path()
    temp_directory.mkdir()
    temp_file = Path(temp_directory.joinpath("fsb.fsb"))

    # copying file to temp directory
    with open(temp_file, "wb") as dest, input_file.open() as fsb_file_io:
        dest.write(fsb_file_io.read())
    input_file.all_done()
    
    # run fsb extractor on fsb file.
    exe_return = subprocess.run([FileManager.LIB_FSB_EXE_FILE, temp_file], shell=True, cwd=temp_directory, capture_output=True)
    if exe_return.returncode != 0:
        raise RuntimeError("EvilFSBExtractor returned a code of %i on file \"%s\"!" % (exe_return.returncode, input_file.name))
    
    # look at what files are there.
    result_file_paths = [result_file for result_file in temp_directory.iterdir() if result_file.name != "fsb.fsb"]
    # return FilePromises
    temp_file.unlink()
    input_file_releases = {result_file_path.name: False for result_file_path in result_file_paths} # the all_done function will set its thing to True, and then delete the folder if all are True.
    return {result_file_path.name: FileManager.FilePromise(FunctionCaller(open, [result_file_path, "rb"]), "%s %s" % (input_file.name, result_file_path.name), "b", FunctionCaller(__output_file_all_done, [input_file_releases, result_file_path])) for result_file_path in result_file_paths}

def extract_fsb_files(files:Iterable[tuple[str,FileManager.FilePromise]]|Generator[tuple[str,FileManager.FilePromise],None,None]) -> Generator[tuple[str,dict[str,FileManager.FilePromise]],None,None]:
    '''Adds all FilePromises to the queue. It yields the input FilePromise name and a dictionary of its result. Does not necessarily maintain the same order.'''
    if not isinstance(files, Iterable):
        raise TypeError("`files` is not an Iterable!")
    for file_name, next_file in files:
        if not isinstance(next_file, FileManager.FilePromise):
            raise TypeError("`files` has an item that is not a FilePromise!")
        yield file_name, extract_fsb_file(next_file)
