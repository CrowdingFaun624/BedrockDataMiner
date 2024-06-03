from typing import TYPE_CHECKING, Any, Literal, overload

from pathlib2 import Path

import Downloader.Manager as Manager
import Utilities.FileManager as FileManager

if TYPE_CHECKING:
    import Version.Version as Version

class Accessor():
    '''
    Base accessor class
    '''

    def __init__(self, name:str, manager:Manager.Manager, version:"Version.Version", file_type_arguments:Any) -> None:
        self.name = name
        self.manager = manager
        self.version = version
        self.initialize()

    def initialize(self) -> None:
        pass

    def modify_file_name(self, file_name:str="") -> str:
        return file_name

    def trim_file_name(self, file_name:str) -> str:
        return file_name

    def install_all(self, destination:Path|None) -> None:
        return self.manager.install_all(destination)

    def file_exists(self, file_name:str) -> bool:
        return self.manager.file_exists(self.modify_file_name(file_name))

    def get_files_in(self, parent:str) -> list[str]:
        return [self.trim_file_name(file) for file in self.manager.get_files_in(self.modify_file_name(parent))]

    def get_file_list(self) -> list[str]:
        return [self.trim_file_name(file) for file in self.manager.get_files_in(self.modify_file_name())]

    def get_full_file_list(self) -> list[str]:
        return self.manager.get_file_list()

    @overload
    def read(self, file_name:str, mode:Literal["b"]) -> bytes: ...
    @overload
    def read(self, file_name:str, mode:Literal["t"]) -> str: ...
    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        return self.manager.read(self.modify_file_name(file_name), mode)

    def get_file(self, file_name:str, mode:Literal["b", "t"]="b") -> FileManager.FilePromise:
        return self.manager.get_file(self.modify_file_name(file_name), mode)

    def all_done(self) -> None:
        return self.manager.all_done()

class SubDirectoryAccessor(Accessor):
    '''
    Accessor for directory access that automatically adds a certain string to the beginning of all paths.
    '''

    file_prepension:str
    '''
    The string to prepend to incoming file names and remove from outgoing file names.
    '''

    def initialize(self) -> None:
        self.file_prepension = ""

    def modify_file_name(self, file_name:str="") -> str:
        return self.file_prepension + file_name

    def trim_file_name(self, file_name:str) -> str:
        return file_name[len(self.file_prepension):]
