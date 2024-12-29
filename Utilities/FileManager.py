import hashlib
import shutil
import uuid
from pathlib import Path

PARENT_DIRECTORY          = Path("./").absolute()
FILE_STORAGE_DIRECTORY    = PARENT_DIRECTORY.joinpath("_assets", "file_storage")
FILE_STORAGE_OBJECTS_DIRECTORY = FILE_STORAGE_DIRECTORY.joinpath("objects")
FILE_STORAGE_INDEX_FILE   = FILE_STORAGE_DIRECTORY.joinpath("index.txt")
LIB_DIRECTORY             = PARENT_DIRECTORY.joinpath("_lib")
LIB_FSB_DIRECTORY         = LIB_DIRECTORY.joinpath("fsb")
LIB_FSB_EXE_FILE          = LIB_FSB_DIRECTORY.joinpath("fsb_aud_extr.exe")
LIB_EXIFTOOL_DIRECTORY    = LIB_DIRECTORY.joinpath("exiftool-12.93_64")
LIB_EXIFTOOL_EXE_FILE     = LIB_EXIFTOOL_DIRECTORY.joinpath("exiftool.exe")
LIB_MATERIAL_BIN_TOOL_DIRECTORY = LIB_DIRECTORY.joinpath("MaterialBinTool")
OUTPUT_DIRECTORY          = PARENT_DIRECTORY.joinpath("_output")
TEMP_DIRECTORY            = PARENT_DIRECTORY.joinpath("_temp")

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
