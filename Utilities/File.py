from typing import Literal, TypedDict

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Types import register_decorator
from Serializer.Serializer import Serializer
from Utilities.CustomJson import Coder
from Utilities.FileStorage import archive_data, read_archived

FileJsonTypedDict = TypedDict("FileJsonTypedDict", {"$special_type": Literal["file"], "hash": str, "name": str})

class FileCoder(Coder[FileJsonTypedDict, "File"]):

    __slots__ = ()

    special_type_name = "file"

    @classmethod
    def decode(cls, data: FileJsonTypedDict, domain:"Domain.Domain") -> "File":
        integer_hash = hash_str_to_int(data["hash"])
        domain.active_file_hashes.add(integer_hash)
        return File(data["name"], data_hash=integer_hash)

    @classmethod
    def encode(cls, data: "File", domain:"Domain.Domain") -> FileJsonTypedDict:
        # files contained by data are archived when the File object is created.
        return {"$special_type": "file", "hash": hash_int_to_str(data.hash), "name": data.display_name}

def new_file(data:bytes, file_name:str, domain:"Domain.Domain") -> "File":
    integer_hash = hash_str_to_int(archive_data(data, file_name))
    domain.active_file_hashes.add(integer_hash)
    return File(file_name, integer_hash)

def hash_int_to_str(hash_int:int) -> str:
    """
    Assumes hash length of 40.
    """
    return hex(hash_int)[2:].zfill(40)

def hash_str_to_int(hash_str:str) -> int:
    return int(hash_str, base=16)

@register_decorator("abstract_file", ..., is_file=True)
class AbstractFile[a]():

    __slots__ = (
        "display_name",
        "hash",
    )

    def __init__(self, display_name:str, data_hash:int) -> None:
        self.display_name = display_name
        self.hash = data_hash

    def read(self, serializer:Serializer|None) -> a:
        ...

    def set_data(self, serializer:Serializer|None, data:a) -> None:
        ...

    def del_data(self, serializer:Serializer|None) -> None:
        ...

    def __eq__(self, other:"AbstractFile") -> bool:
        return self is other or hash(self) == hash(other)

    def __hash__(self) -> int:
        return self.hash

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.display_name}\" hash {hash_int_to_str(self.hash)}>"

@register_decorator("file", None, json_coder=FileCoder)
class File[a](AbstractFile[a]):

    __slots__ = (
        "_bytes",
        "_data",
    )

    def __init__(self, display_name:str, data_hash:int) -> None:
        super().__init__(display_name, data_hash)
        self._bytes:bytes|None = None
        self._data:dict[Serializer,a] = {}

    @property
    def bytes(self) -> bytes:
        if self._bytes is None:
            self._bytes = read_archived(hash_int_to_str(self.hash))
        return self._bytes

    def read(self, serializer:Serializer|None) -> a:
        # installs data without returning anything.
        if serializer is None:
            raise Exceptions.SerializerNoneError(self)
        if (data := self._data.get(serializer, ...)) is not ...:
            return data
        try:
            self._data[serializer] = data = serializer.deserialize(self.bytes)
            if data is ...:
                raise Exceptions.SerializerEllipsisError(self, serializer)
            return data
        except Exception:
            raise Exceptions.SerializationFailureError(serializer, self.display_name)

    def set_data(self, serializer:Serializer|None, data:a) -> None:
        # modifies data, and *does not* change the hash of this File.
        if serializer is None:
            raise Exceptions.SerializerNoneError(self)
        if data is ...:
            raise Exceptions.SerializerEllipsisError(self, None)
        self._data[serializer] = data

    def del_data(self, serializer:Serializer|None) -> None:
        # in case you want to clear up memory or something.
        if serializer is None:
            raise Exceptions.SerializerNoneError(self)
        del self._data[serializer]

@register_decorator("fake_file", None)
class FakeFile[a](AbstractFile[a]):
    """
    Similar to a File, but it can be created anywhere and using any hash/data.
    """

    __slots__ = (
        "_data"
    )

    def __init__(self, display_name: str, data:a, serializer:Serializer|None, data_hash: int) -> None:
        super().__init__(display_name, data_hash)
        if data is ...:
            raise Exceptions.SerializerEllipsisError(self, serializer)
        self._data = {serializer: data}

    def read(self, serializer: Serializer|None) -> a:
        if (output := self._data.get(serializer, ...)) is ...:
            raise Exceptions.FileWrongSerializerError(self, list(self._data.keys()), serializer)
        return output

    def set_data(self, serializer: Serializer|None, data: a) -> None:
        if data is ...:
            raise Exceptions.SerializerEllipsisError(self, serializer)
        self._data[serializer] = data

    def del_data(self, serializer: Serializer|None) -> None:
        del self._data[serializer]
