from typing import AnyStr, Generic, Literal, cast, overload

import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager


def new_file(data:bytes, mode:Literal["b", "t"], file_name:str) -> "File":
    if len(data) == 0:
        raise Exceptions.EmptyFileError(message="(file \"%s\")" % (file_name,))
    file_hash = FileStorageManager.archive_data(data, file_name)
    return File(mode, data_hash=file_hash) # not create with value argument to not clog the memory.

class File(Generic[AnyStr]):

    @overload
    def __init__(self:"File[bytes]", mode:Literal["b"], *, data_hash:str|None=None, value:bytes|None=None) -> None: ...
    @overload
    def __init__(self:"File[str]", mode:Literal["t"], *, data_hash:str|None=None, value:str|None=None) -> None: ...
    def __init__(self, mode:Literal["b", "t"], *, data_hash:str|None=None, value:str|bytes|None=None) -> None:
        self.mode:Literal["b", "t"] = mode
        if data_hash is not None and value is not None:
            self.value = value
            self.hash = data_hash
        elif data_hash is not None and value is None:
            self.hash = data_hash
            self.value = None
        elif data_hash is None and value is not None:
            self.value = value
            if isinstance(value, str):
                self.hash = FileManager.stringify_sha1_hash(FileManager.get_hash_from_bytes(value.encode()))
            else:
                self.hash = FileManager.stringify_sha1_hash(FileManager.get_hash_from_bytes(value))
        elif data_hash is None and value is None:
            raise Exceptions.FileInvalidArgumentsError(self)

    def read(self) -> AnyStr:
        if self.value is None:
            self.value = FileStorageManager.read_archived(self.hash, self.mode)
        return cast(AnyStr, self.value)

    def open(self) -> FileManager.FilePromise:
        return FileStorageManager.open_archived(self.hash, self.mode)

    def __eq__(self, other:"File") -> bool:
        return self is other or self.value == other.value

    def __hash__(self) -> int:
        return hash(self.hash)

    def __repr__(self) -> str:
        if self.value is None:
            return "<%s hash %s>" % (self.__class__.__name__, self.hash)
        else:
            return "<%s len %i hash %s>" % (self.__class__.__name__, len(self.value), self.hash)
