import bisect
from typing import Callable, Iterable

import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Downloader.DirectoryAccessor as DirectoryAccessor

location_value_function:Callable[[str,str],tuple[bool,str]] = lambda key, value: (len(value) == 0 or value.endswith("/"), "location does not end in \"/\"")
location_item_function:Callable[[str],tuple[bool,str]] = lambda item: (len(item) == 0 or item.endswith("/"), "location does not end in \"/\"")
suffix_function:Callable[[str],tuple[bool,str]] = lambda item: (item.startswith("."), "suffix does not start with \".\"")

class FileSet():

    def __init__(self, files:Iterable[str]) -> None:
        self.files = sorted(files) # must be sorted for bisection
        self.file_set = set(files)

    def __iter__(self) -> Iterable[str]:
        yield from self.files

    def get_files_in(self, directory:str) -> list[str]:
        '''Returns all file names that start with the directory string.'''
        directory_length = len(directory)
        left = bisect.bisect_left(self.files, directory)
        right = bisect.bisect_right(self.files, directory, lo=left, key=lambda item: item[:directory_length])
        return self.files[left:right]

    def file_exists(self, file:str) -> bool:
        return file in self.file_set

class FileDataminer(Dataminer.Dataminer):

    serializer_names = {"main"}

    def get_coverage(self, file_set:FileSet, environment:DataminerEnvironment.DataminerEnvironment) -> set[str]:
        '''
        Must be overridden by subclasses of FileDataminer.
        Returns the set of file paths this Dataminer would return if it were
        activated.

        :file_set: The set of all file paths.
        :environment: The DataminerEnvironment to use (for dependencies).
        '''
        ...
