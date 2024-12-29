import hashlib
import shutil
import uuid
from pathlib import Path

PARENT_DIRECTORY          = Path("./").absolute()
COMPARISONS_DIRECTORY     = PARENT_DIRECTORY.joinpath("_comparisons")
DOMAINS_DIRECTORY         = PARENT_DIRECTORY.joinpath("_domains")
FILE_STORAGE_DIRECTORY    = PARENT_DIRECTORY.joinpath("_file_storage")
FILE_STORAGE_OBJECTS_DIRECTORY = FILE_STORAGE_DIRECTORY.joinpath("objects")
FILE_STORAGE_INDEX_FILE   = FILE_STORAGE_DIRECTORY.joinpath("index.txt")
LIB_DIRECTORY             = PARENT_DIRECTORY.joinpath("_lib")
LIB_MATERIAL_BIN_TOOL_DIRECTORY = LIB_DIRECTORY.joinpath("MaterialBinTool")
OUTPUT_DIRECTORY          = PARENT_DIRECTORY.joinpath("_output")
TEMP_DIRECTORY            = PARENT_DIRECTORY.joinpath("_temp")
VERSIONS_DIRECTORY        = PARENT_DIRECTORY.joinpath("_versions")

def get_temp_file_path() -> Path:
    '''Returns a path such as `./_temp/a6f780a3-83d0-4afd-a654-dc28df0b9831`.'''
    return TEMP_DIRECTORY.joinpath(str(uuid.uuid4()))

def get_hash_hexdigest(file:bytes) -> str:
    '''
    Returns the sha1 hash of bytes in the form of a hexadecimal string.
    '''
    return hashlib.sha1(file).hexdigest()

def get_hash_int(file:bytes) -> int:
    '''
    Returns the sha1 hash of bytes in the form of an integer.
    '''
    return int.from_bytes(hashlib.sha1(file).digest())

def clear_temp() -> None:
    '''
    Removes every file and recursively removes every directory from the temp directory.
    '''
    for file in TEMP_DIRECTORY.iterdir():
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

clear_temp()
