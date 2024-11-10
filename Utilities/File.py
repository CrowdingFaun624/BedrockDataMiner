from types import EllipsisType
from typing import Any, Generic, Iterator, TypeVar

import Serializer.Serializer as Serializer
import Structure.DataPath as DataPath
import Structure.Difference as D
import Utilities.Exceptions as Exceptions
import Utilities.FileStorageManager as FileStorageManager


def new_file(data:bytes, file_name:str, serializer:Serializer.Serializer) -> "File":
    if not serializer.empty_okay and len(data) == 0:
        raise Exceptions.EmptyFileError(message="(file \"%s\")" % (file_name,))
    file_hash = hash_str_to_int(FileStorageManager.archive_data(data, file_name, empty_okay=serializer.empty_okay))
    return File(file_name, serializer, file_hash) # not create with value argument to not clog the memory.

a = TypeVar("a")

def hash_int_to_str(hash_int:int) -> str:
    '''Assumes hash length of 40'''
    return hex(hash_int)[2:].zfill(40)

def hash_str_to_int(hash_str:str) -> int:
    return int(hash_str, base=16)

class AbstractFile(Generic[a]):

    data:a

    def __init__(self, display_name:str, data_hash:int) -> None:
        self.display_name = display_name
        self.hash = data_hash

    def read(self) -> None:
        ...

    def __eq__(self, other:"AbstractFile") -> bool:
        return self is other or self.hash == other.hash

    def __hash__(self) -> int:
        return self.hash

    def __repr__(self) -> str:
        return "<%s \"%s\" hash %s>" % (self.__class__.__name__, self.display_name, hash_int_to_str(self.hash))

    def get_referenced_files(self) -> Iterator[int]:
        '''
        Uses the Serializer of this File to find any filse within it.
        '''
        return; yield

class File(AbstractFile[a]):

    def __init__(self, display_name:str, serializer:Serializer.Serializer, data_hash:int) -> None:
        super().__init__(display_name, data_hash)
        self.serializer = serializer
        self._data:a|EllipsisType = ...

    def read(self) -> None:
        # installs data without returning anything.
        self.data

    def _get_data(self) -> a:
        if self._data is ...:
            file_bytes = FileStorageManager.read_archived(hash_int_to_str(self.hash), "b")
            try:
                data:a = self.serializer.deserialize(file_bytes)
                self._data = data
            except Exception:
                raise Exceptions.SerializationFailureError(self.serializer, self.display_name, "(in File.read)")
        return self._data

    def _set_data(self, data:a) -> None:
        # modifies data, and *does not* change the hash of this File.
        self._data = data

    def _del_data(self) -> None:
        # in case you want to clear up memory or something.
        self._data = ...

    data = property(_get_data, _set_data, _del_data)

    def get_referenced_files(self) -> Iterator[int]:
        if self.serializer.can_contain_subfiles:
            file_bytes = FileStorageManager.read_archived(hash_int_to_str(self.hash), "b")
            yield from self.serializer.get_referenced_files(file_bytes)

class EmptyFile(File[a]):

    def __init__(
        self,
        serializer:Serializer.Serializer,
        data_hash:int,
        data:a|EllipsisType=..., # type: ignore idk
    ) -> None:
        super().__init__("empty_file", serializer, data_hash)
        # when data is needed, it will read the file at `data_hash` using `serializer`, but
        # then replace it with data of same type but empty.
        if data is ...:
            self._data:a|EllipsisType = ...
        else:
            self._data:a|EllipsisType = type(data)()

    def __hash__(self) -> int:
        # must have a different hash than the creating file for caching reasons
        # but must remember what hash the creating file had so it knows the
        # data type.
        return 0

    def _get_data(self) -> a:
        if self._data is ...:
            data:a = super()._get_data()
            self._data = type(data)()
        return self._data

class FakeFile(AbstractFile[a]):
    '''Similar to a File, but it can be created anywhere and using any hash/data.'''

    def __init__(self, display_name: str, data:a, data_hash: int) -> None:
        super().__init__(display_name, data_hash)
        self.data = data

class FileDiff(Generic[a]):
    '''
    Similar to a FakeFile, but contains the data from two files.
    This exists because it's easier to hash or something.
    '''

    def __init__(self, file1:AbstractFile[a], file2:AbstractFile[a], data:a|D.Diff[a,a]) -> None:
        self.data = data
        self.display_name1 = file1.display_name
        self.display_name2 = file2.display_name
        self.hash = hash((file1, file2))

    def __hash__(self) -> int:
        return self.hash

    def __repr__(self) -> str:
        if self.display_name1 == self.display_name2:
            return "<%s \"%s\" hash %s>" % (self.__class__.__name__, self.display_name1, hash_int_to_str(self.hash))
        else:
            return "<%s \"%s\" and \"%s\" hash %s>" % (self.__class__.__name__, self.display_name1, self.display_name2, hash_int_to_str(self.hash))

NoneType = type(None)

def recursive_examine_data_for_files(data:Any) -> Iterator[int]:
    match data:
        case int() | str() | float() | bool() | NoneType():
            return
        case dict():
            for value in data.values():
                yield from recursive_examine_data_for_files(value)
        case list():
            for value in data:
                yield from recursive_examine_data_for_files(value)
        case AbstractFile():
            yield data.hash
            yield from data.get_referenced_files()
        case DataPath.DataPath():
            yield from recursive_examine_data_for_files(data.embedded_data)
        case _:
            raise TypeError("How do I recursively examine type %s for files?" % (data.__class__.__name__,))
