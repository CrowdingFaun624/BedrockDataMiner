from types import EllipsisType
from typing import Generic, TypeVar

import Serializer.Serializer as Serializer
import Utilities.Exceptions as Exceptions
import Utilities.FileStorageManager as FileStorageManager


def new_file(data:bytes, file_name:str, serializer:Serializer.Serializer) -> "File":
    if len(data) == 0:
        raise Exceptions.EmptyFileError(message="(file \"%s\")" % (file_name,))
    file_hash = hash_str_to_int(FileStorageManager.archive_data(data, file_name))
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

class FakeFile(AbstractFile[a]):
    '''Similar to a File, but it can be created anywhere and using any hash/data.'''
    
    def __init__(self, display_name: str, data:a, data_hash: int) -> None:
        super().__init__(display_name, data_hash)
        self.data = data
