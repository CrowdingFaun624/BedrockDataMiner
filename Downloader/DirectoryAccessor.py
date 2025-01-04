import bisect

import Downloader.Accessor as Accessor


class DirectoryAccessor(Accessor.Accessor):

    @property
    def file_list(self) -> list[str]: ...

    @property
    def full_file_list(self) -> list[str]:
        return self.file_list

    def file_exists(self, file_name:str) -> bool: ...

    def read(self, file_name:str) -> bytes: ...

    def get_files_in(self, parent:str) -> list[str]:
        '''Returns a list of all files that are within the given directory.'''
        directory_length = len(parent)
        file_list = self.file_list
        left = bisect.bisect_left(file_list, parent)
        right = bisect.bisect_right(file_list, parent, lo=left, key=lambda item: item[:directory_length])
        return file_list[left:right]
