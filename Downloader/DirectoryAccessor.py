import bisect
from typing import BinaryIO, Sequence

import Downloader.Accessor as Accessor


class DirectoryAccessor(Accessor.Accessor):

    __slots__ = ()

    @property
    def file_list(self) -> Sequence[str]: ...

    def file_exists(self, file_name:str) -> bool: ...

    def read(self, file_name:str) -> bytes: ...

    def open(self, file_name:str) -> BinaryIO: ...

    def get_files_in(self, parent:str) -> Sequence[str]:
        '''Returns a list of all files that are within the given directory.'''
        directory_length = len(parent)
        file_list = self.file_list
        left = bisect.bisect_left(file_list, parent)
        right = bisect.bisect_right(file_list, parent, lo=left, key=lambda item: item[:directory_length])
        return file_list[left:right]
