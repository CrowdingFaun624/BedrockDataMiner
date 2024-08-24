import traceback
from typing import (IO, Any, Callable, Literal, Mapping, Sequence, TypeVar,
                    overload)

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager

read_files_typevar = TypeVar("read_files_typevar")

location_value_function:Callable[[str,str],tuple[bool,str]] = lambda key, value: (len(value) == 0 or value.endswith("/"), "location does not end in \"/\"")
location_item_function:Callable[[str],tuple[bool,str]] = lambda item: (len(item) == 0 or item.endswith("/"), "location does not end in \"/\"")
suffix_function:Callable[[str],tuple[bool,str]] = lambda item: (item.startswith("."), "suffix does not start with \".\"")

class FileDataMiner(DataMiner.DataMiner):

    requires_serializer = True

    def get_coverage(self, file_set:set[str], environment:DataMinerEnvironment.DataMinerEnvironment) -> set[str]:
        '''
        Must be overridden by subclasses of FileDataMiner.
        Returns the set of file paths this DataMiner would return if it were
        activated.\n
        :file_set: The set of all file paths.
        :environment: The DataMinerEnvironment to use (for dependencies).
        '''
        ...

    def get_files_in(self, accessor:Accessor.DirectoryAccessor, parent:str) -> list[str]:
        return accessor.get_files_in(parent)

    def get_file_list(self, accessor:Accessor.DirectoryAccessor) -> list[str]:
        return accessor.get_file_list()

    @overload
    def read_file(self, accessor:Accessor.DirectoryAccessor, file_name:str, mode:Literal["b"]) -> bytes: ...
    @overload
    def read_file(self, accessor:Accessor.DirectoryAccessor, file_name:str, mode:Literal["t"]) -> str: ...
    @overload
    def read_file(self, accessor:Accessor.DirectoryAccessor, file_name:str) -> str: ...
    def read_file(self, accessor:Accessor.DirectoryAccessor, file_name:str, mode:Literal["b", "t"]="t") -> str|bytes:
        return accessor.read(file_name, mode)

    @overload
    def read_files(self, accessor:Accessor.DirectoryAccessor, files:Sequence[str], non_exist_ok:bool=False) -> dict[str,str]: ...
    @overload
    def read_files(self, accessor:Accessor.DirectoryAccessor, files:Sequence[tuple[str,Literal["t"],None]], non_exist_ok:bool=False) -> dict[str,str]: ...
    @overload
    def read_files(self, accessor:Accessor.DirectoryAccessor, files:Sequence[tuple[str,Literal["b"],None]], non_exist_ok:bool=False) -> dict[str,bytes]: ...
    @overload
    def read_files(self, accessor:Accessor.DirectoryAccessor, files:Sequence[tuple[str,Literal["t"],Callable[[IO[str]],read_files_typevar]]], non_exist_ok:bool=False) -> dict[str,read_files_typevar]: ...
    @overload
    def read_files(self, accessor:Accessor.DirectoryAccessor, files:Sequence[tuple[str,Literal["b"],Callable[[IO[bytes]],read_files_typevar]]], non_exist_ok:bool=False) -> dict[str,read_files_typevar]: ...
    @overload
    def read_files(self, accessor:Accessor.DirectoryAccessor, files:Sequence[str|tuple[str,Literal["b", "t"],None|Callable[[IO],read_files_typevar]]], non_exist_ok:bool=False) -> Mapping[str,str|bytes|read_files_typevar]: ...
    def read_files(self, accessor:Accessor.DirectoryAccessor, files:Sequence[str|tuple[str,Literal["b", "t"],None|Callable[[IO],read_files_typevar]]], non_exist_ok:bool=False) -> Mapping[str,str|bytes|read_files_typevar]:
        '''Synchronously obtains a list of files. Items of the list can be a filename string or (filename string, mode, optional_callable).
        The optional callable takes in an IO object and returns a transformed value.'''

        DEFAULT_MODE = "t"
        normalized_files:list[tuple[str,Literal["b", "t"],None|Callable[[IO],Any]]] = [(file, DEFAULT_MODE, None) if isinstance(file, str) else file for file in files]

        exceptions:list[tuple[str, Exception]] = []
        file_results:dict[str,str|bytes|read_files_typevar] = {}
        for file_name, file_mode, callable in normalized_files:
            try:
                if not non_exist_ok or self.file_exists(accessor, file_name):
                    if callable is None:
                        file_result = self.read_file(accessor, file_name, file_mode)
                    else:
                        file = self.get_file(accessor, file_name, file_mode)
                        with file.open() as f:
                            file_result = callable(f)
                        file.all_done()
                    file_results[file_name] = file_result
                else: # file does not exist
                    pass
            except Exception as e:
                exceptions.append((file_name, e))

        for file_name, exception in exceptions:
            print("Failed to get file \"%s\"!" % file_name)
            traceback.print_exception(exception)
            print()
        if len(exceptions) > 0:
            raise Exceptions.DataMinerReadFilesError(self)

        return file_results

    def file_exists(self, accessor:Accessor.DirectoryAccessor, file_name:str) -> bool:
        return accessor.file_exists(file_name)

    def get_file(self, accessor:Accessor.DirectoryAccessor, file_name:str, mode:Literal["b","t"]="t") -> FileManager.FilePromise:
        return accessor.get_file(file_name, mode)