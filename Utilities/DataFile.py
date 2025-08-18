from pathlib import Path
from typing import Any

import pyjson5 as pyjson5

from Utilities.Exceptions import DataFileNothingToWriteError


class DataFile():

    __slots__ = (
        "_contents",
        "file_name",
        "file_path",
        "has_read_contents",
    )

    def __init__(self, path:Path, file_name:str) -> None:
        self.file_name = file_name
        self.file_path = path
        self.has_read_contents = False
        self._contents:Any|None = None

    @property
    def contents(self) -> Any:
        """
        The contents of the DataFile. Waits until first access to read.
        """
        if not self.has_read_contents:
            with open(self.file_path, "rt") as f:
                self._contents = pyjson5.load(f)
            self.has_read_contents = True
        return self._contents

    def write(self, obj:object=...) -> None:
        """
        Re-writes the content to the file.

        :param obj: The object to replace the content with (optional).
        """
        if obj is not ...:
            self._contents = obj
        elif not self.has_read_contents:
            raise DataFileNothingToWriteError(self)
        with open(self.file_path, "wt") as f:
            pyjson5.dump(self._contents, f)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.file_name}>"
