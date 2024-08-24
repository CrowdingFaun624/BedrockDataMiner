from typing import Generic, TypeVar

import Serializer.Serializer as Serializer
import Utilities.Exceptions as Exceptions
import Utilities.FileStorageManager as FileStorageManager


def new_file(data:bytes, file_name:str, serializer:Serializer.Serializer) -> "File":
    if len(data) == 0:
        raise Exceptions.EmptyFileError(message="(file \"%s\")" % (file_name,))
    file_hash = FileStorageManager.archive_data(data, file_name)
    return File(file_name, serializer, file_hash) # not create with value argument to not clog the memory.

a = TypeVar("a")

class File(Generic[a]):

    def __init__(self, display_name:str, serializer:Serializer.Serializer, data_hash:str) -> None:
        self.display_name = display_name
        self.serializer = serializer
        self.hash = data_hash
        self.value:a|None = None

    def read(self) -> a:
        if self.value is None:
            file_bytes = FileStorageManager.read_archived(self.hash, "b")
            try:
                data:a = self.serializer.deserialize(file_bytes)
                self.value = data
            except Exception:
                raise Exceptions.SerializationFailureError(self.serializer, self.display_name, "(in File.read)")
        return self.value

    def __eq__(self, other:"File") -> bool:
        return self is other or self.value == other.value

    def __hash__(self) -> int:
        return hash(self.hash)

    def __repr__(self) -> str:
        return "<%s \"%s\" hash %s>" % (self.__class__.__name__, self.display_name, self.hash)
