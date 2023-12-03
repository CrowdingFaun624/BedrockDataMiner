import errno
import os
import shutil
import sys

from pathlib2 import Path

PARENT_FOLDER          = Path("./").absolute()
print(PARENT_FOLDER)
ASSETS_FOLDER          = Path(PARENT_FOLDER.joinpath("_assets"))
STORED_VERSIONS_FOLDER = Path(ASSETS_FOLDER.joinpath("stored_versions"))
STORED_VERSIONS_OBJECTS_FOLDER = Path(STORED_VERSIONS_FOLDER.joinpath("objects"))
STORED_VERSIONS_INDEXES_FILE = Path(STORED_VERSIONS_FOLDER.joinpath("indexes.zip"))
STORED_VERSIONS_INPUT_FOLDER = Path(STORED_VERSIONS_FOLDER.joinpath("input"))
STORED_VERSIONS_OUTPUT_FOLDER = Path(STORED_VERSIONS_FOLDER.joinpath("output"))
VERSIONS_FILE          = Path(ASSETS_FOLDER.joinpath("versions.json"))
VERSION_PARSER_WARNINGS_FILE = Path(ASSETS_FOLDER.joinpath("version_parser_warnings.txt"))
WIKI_VALIDATOR_WARNINGS_FILE = Path(ASSETS_FOLDER.joinpath("wiki_validator_warnings.txt"))
TEMP_FOLDER            = Path(PARENT_FOLDER.joinpath("_temp"))
VERSIONS_FOLDER        = Path(PARENT_FOLDER.joinpath("_versions"))

def get_version_path(version_name:str) -> Path:
    version_path = Path(VERSIONS_FOLDER.joinpath(version_name))
    if VERSIONS_FOLDER not in version_path.parents:
        raise FileNotFoundError("Version \"%s\"'s folder can not be created due to illegal characters!" % version_name)
    return version_path

def get_version_install_path(version_folder:Path) -> Path:
    return Path(version_folder.joinpath("client"))

def get_version_data_path(version_folder:Path, file_name:str) -> Path:
    data_path = Path(version_folder.joinpath("/data/%s" % file_name))
    if version_folder not in data_path.parents:
        raise FileNotFoundError("Data file \"%s\" has an invalid name!" % file_name)
    return data_path

def is_pathname_valid(pathname:str) -> bool: # https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
    '''Returns True if the path name is valid on this OS.'''
    ERROR_INVALID_NAME = 123
    try:
        if not isinstance(pathname, str) or not pathname:
            return False
        _, pathname = os.path.splitdrive(pathname)
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError as exc:
        return False
    else:
        return True

def clear_temp() -> None:
    for file in TEMP_FOLDER.iterdir():
        file:Path
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

clear_temp()