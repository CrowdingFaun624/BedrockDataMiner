from pathlib2 import Path
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    import Utilities.FileManager as FileManager
    import Utilities.Version as Version

class InstallManager():

    def __init__(self, version:"Version.Version", location:Path) -> None:
        '''
        :version: Version object this manager is based on.
        :location: File location to the folder containing extracted files.'''

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

    def install(self, file_name:str, destination:Path|None=None) -> Path:
        '''Installs the given file name from the Version. Returns its destination.'''
        raise NotImplementedError("`install` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def file_exists(self, name:str) -> bool:
        '''Returns if the file exists in this version.'''
        raise NotImplementedError("`file_exists` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def get_files_in(self, parent:str) -> Iterable[str]:
        '''Returns a list of all files that are within the given directory.'''
        raise NotImplementedError("`get_files_in` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def get_file_list(self) -> list[str]:
        '''Returns a list of all files in the archive.'''
        raise NotImplementedError("`get_file_list` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def get_full_file_list(self) -> list[str]:
        '''Returns a list of every file in the archive, including those not in the assets folder.'''
        raise NotImplementedError("`get_file_list` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def read(self, file_name:str, mode:str="b") -> bytes|str:
        '''Returns the contents of the given file name from the Version'''
        raise NotImplementedError("`read` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def get_file(self, file_name:str, mode:str="b", is_in_assets:bool=True) -> "FileManager.FilePromise":
        '''Returns a FilePromise object of the file.'''
        raise NotImplementedError("`get_file` is not implemented for \"%s\"'s InstallManager!" % self.version.name)

    def all_done(self) -> None:
        '''Removes all files that were created as part of the installation of this version.'''
        raise NotImplementedError("`get_file` is not implemented for \"%s\"'s InstallManager!" % self.version.name)
