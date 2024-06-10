from typing import TYPE_CHECKING, Any, Literal, overload

from pathlib2 import Path

import Utilities.Exceptions as Exceptions
import Version.VersionTags as VersionTags

if TYPE_CHECKING:
    import Utilities.FileManager as FileManager
    import Version.Version as Version

class Manager():

    def __init__(self, version:"Version.Version", file_type_arguments:dict[str,Any], location:Path, version_tags:VersionTags.VersionTags) -> None:
        '''
        :version: Version object this manager is based on.
        :location: File location to the directory containing extracted files.
        '''
        self.version = version
        self.location = location
        self.prepare_for_install(version_tags, file_type_arguments)

    def __repr__(self) -> str:
        return "<%s for %s>" % (self.__class__.__name__, self.version.name)

    def prepare_for_install(self, version_tags:VersionTags.VersionTags, file_type_parameters:dict[str,Any]) -> None:
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
        raise Exceptions.ManagerUndefinedMethodError(self, self.get_files_in)

    def get_file_list(self) -> list[str]:
        '''Returns a list of all files in the archive.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.get_file_list)

    @overload
    def read(self, file_name:str, mode:Literal["b"]) -> bytes: ...
    @overload
    def read(self, file_name:str, mode:Literal["t"]) -> str: ...
    def read(self, file_name:str, mode:Literal["b","t"]="b") -> bytes|str:
        '''Returns the contents of the given file name from the Version'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.read)

    def get_file(self, file_name:str, mode:Literal["b","t"]="b") -> "FileManager.FilePromise":
        '''Returns a FilePromise object of the file.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.get_file)

    def all_done(self) -> None:
        '''Removes all files that were created as part of the installation of this version.'''
        raise Exceptions.ManagerUndefinedMethodError(self, self.all_done)
