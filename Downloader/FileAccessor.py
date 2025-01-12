from typing import BinaryIO

import Downloader.Accessor as Accessor


class FileAccessor(Accessor.Accessor):

    __slots__ = ()

    def read(self) -> bytes:
        with self.open() as f:
            return f.read()

    def open(self) -> BinaryIO: ...
