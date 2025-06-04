from typing import BinaryIO

from Downloader.Accessor import Accessor


class FileAccessor(Accessor):

    __slots__ = ()

    def read(self) -> bytes:
        with self.open() as f:
            return f.read()

    def open(self) -> BinaryIO: ...
