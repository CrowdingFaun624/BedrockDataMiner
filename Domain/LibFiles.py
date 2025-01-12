from pathlib import Path

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions


class LibFiles():

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name}>"

    def __getitem__(self, name:str) -> Path:
        path = self.domain.lib_directory.joinpath(name)
        if not path.exists():
            raise Exceptions.LibFileNotFoundError(name, path)
        elif self.domain.lib_directory not in path.parents:
            raise Exceptions.LibFileWrongDirectoryError(name, path, self.domain.lib_directory)
        else:
            return path

    def get[A](self, name:str, default:A=None, wrong_directory_okay:bool=False) -> Path|A:
        path = self.domain.lib_directory.joinpath(name)
        if not path.exists():
            return default
        elif (wrong_directory := self.domain.lib_directory not in path.parents) and wrong_directory_okay:
            return default
        elif wrong_directory and not wrong_directory_okay:
            raise Exceptions.LibFileWrongDirectoryError(name, path, self.domain.lib_directory)
        else:
            return path
