import bisect
from pathlib import Path
from typing import TYPE_CHECKING, Any

import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Utilities.FileManager as FileManager
    import Version.Version as Version

class Manager():

    def __init__(self, version:"Version.Version", file_type_arguments:dict[str,Any], location:Path) -> None:
        '''
        :version: Version object this manager is based on.
        :location: File location to the directory containing extracted files.
        '''
        self.version = version
        self.location = location
        self.prepare_for_install(file_type_arguments)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} for {self.version.name}>"

    def prepare_for_install(self, file_type_parameters:dict[str,Any]) -> None:
        '''Any actions that can take place before grabbing files can happen.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.prepare_for_install)

    def install_all(self, destination:Path|None=None) -> None:
        '''Installs all of the files of the Version.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.install_all)

    def file_exists(self, file_name:str) -> bool:
        '''Returns if the file exists in this version.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.file_exists)

    def get_files_in(self, parent:str) -> list[str]:
        '''Returns a list of all files that are within the given directory.'''
        directory_length = len(parent)
        file_list = self.get_file_list()
        left = bisect.bisect_left(file_list, parent)
        right = bisect.bisect_right(file_list, parent, lo=left, key=lambda item: item[:directory_length])
        return file_list[left:right]

    def get_file_list(self) -> list[str]:
        '''Returns a sorted list of all files in the archive.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.get_file_list)

    def read(self, file_name:str) -> bytes:
        '''Returns the contents of the given file name from the Version'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.read)

    def all_done(self) -> None:
        '''Removes all files that were created as part of the installation of this version.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.all_done)
