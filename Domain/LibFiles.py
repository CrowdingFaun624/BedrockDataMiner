from pathlib import Path

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions


class LibFiles():

    __slots__ = (
        "_all_files",
        "domain",
    )

    def __init__(self, domain:"Domain.Domain") -> None:
        self._all_files:list[Path]|None = None
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name}>"

    @property
    def all_files(self) -> list[Path]:
        if self._all_files is None:
            self._all_files = list(self.domain.lib_directory.rglob("*"))
        return self._all_files

    def __getitem__(self, name:str) -> Path:
        path = self.domain.lib_directory.joinpath(name)
        if not path.exists():
            raise Exceptions.LibFileNotFoundError(name, path, [file.relative_to(self.domain.lib_directory).as_posix() for file in self.all_files])
        elif self.domain.lib_directory not in path.parents:
            raise Exceptions.LibFileWrongDirectoryError(name, path, self.domain.lib_directory, [file.relative_to(self.domain.lib_directory).as_posix() for file in self.all_files])
        else:
            return path

    def get[A](self, name:str, default:A=None, wrong_directory_okay:bool=False) -> Path|A:
        path = self.domain.lib_directory.joinpath(name)
        if not path.exists():
            return default
        elif (wrong_directory := self.domain.lib_directory not in path.parents) and wrong_directory_okay:
            return default
        elif wrong_directory and not wrong_directory_okay:
            raise Exceptions.LibFileWrongDirectoryError(name, path, self.domain.lib_directory, [file.relative_to(self.domain.lib_directory).as_posix() for file in self.all_files])
        else:
            return path
