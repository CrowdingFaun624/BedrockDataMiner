from pathlib2 import Path
from typing import IO

import Utilities.Version as Version

class InstallManager():
    def __init__(self, version:Version.Version, location:Path) -> None:
        '''
        :version: Version object this manager is based on.
        :location: File location to the folder containing extracted files.'''

        if not isinstance(version, Version.Version):
            raise TypeError("Parameter `version` is not a `Version`!")
        if not isinstance(location, Path):
            raise TypeError("Parameter `location` is not a `Path`!")

        self.version = version
        self.location = location
        self.prepare_for_install()
    
    def get_full_file_name(self, asset_name:str) -> str:
        '''Returns the full file path within the archive needed to find the given asset.'''
        raise NotImplementedError("`get_full_file_name` is not implemented for \"%s\"'s InstallManager!" % self.version.name)
    
    def prepare_for_install(self) -> None:
        '''Any actions that can take place before grabbing files can happen.'''
        raise NotImplementedError("`prepare_for_install` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def install_all(self, destination:Path|None=None) -> None:
        '''Installs all of the files of the Version.'''
        raise NotImplementedError("`install_all` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def install(self, file_name:str, destination:Path|None=None) -> None:
        '''Installs the given file name from the Version.'''
        raise NotImplementedError("`install` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def read(self, file_name:str, mode:str="b") -> bytes|str:
        '''Returns the contents of the given file name from the Version'''
        raise NotImplementedError("`read` is not implemented for \"%s\"'s InstallManager!" % self.version.name)
    
    def get_file(self, file_name:str, mode:str="b") -> IO:
        '''Returns an IO object of the file.'''
        raise NotImplementedError("`get_file` is not implemented for \"%s\"'s InstallManager!" % self.version.name)
