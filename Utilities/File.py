from types import EllipsisType
from typing import Any, Iterator, Literal, TypedDict

import Component.Types as Types
import Serializer.Serializer as Serializer
import Structure.DataPath as DataPath
import Structure.Difference as D
import Utilities.CustomJson as CustomJson
import Utilities.Exceptions as Exceptions
import Utilities.FileStorageManager as FileStorageManager

FileJsonTypedDict = TypedDict("FileJsonTypedDict", {"$special_type": Literal["file"], "hash": str, "name": str, "serializer": str})

class FileCoder(CustomJson.Coder[FileJsonTypedDict, "File"]):

    special_type_name = "file"

    @classmethod
    def decode(cls, data: FileJsonTypedDict) -> "File":
        import Component.Importer as Importer
        serializer = Importer.serializers.get(data["serializer"])
        if serializer is None:
            raise Exceptions.UnrecognizedSerializerInFileError(data)
        return File(data["name"], serializer, data_hash=hash_str_to_int(data["hash"]))

    @classmethod
    def encode(cls, data: "File") -> FileJsonTypedDict:
        # files contained by data are archived when the File object is created.
        return {"$special_type": "file", "hash": hash_int_to_str(data.hash), "name": data.display_name, "serializer": data.serializer.name}

def new_file(data:bytes, file_name:str, serializer:Serializer.Serializer) -> "File":
    if not serializer.empty_okay and len(data) == 0:
        raise Exceptions.EmptyFileError(message=f"(file \"{file_name}\")")
    file_hash = hash_str_to_int(FileStorageManager.archive_data(data, file_name, empty_okay=serializer.empty_okay))
    return File(file_name, serializer, file_hash) # not create with value argument to not clog the memory.

def hash_int_to_str(hash_int:int) -> str:
    '''Assumes hash length of 40'''
    return hex(hash_int)[2:].zfill(40)

def hash_str_to_int(hash_str:str) -> int:
    return int(hash_str, base=16)

@Types.register_decorator("abstract_file", hashing_method=hash, is_file=True)
class AbstractFile[a]():

    data:a

    __slots__ = (
        "display_name",
        "hash",
    )

    def __init__(self, display_name:str, data_hash:int) -> None:
        self.display_name = display_name
        self.hash = data_hash

    def read(self) -> None:
        ...

    def __eq__(self, other:"AbstractFile") -> bool:
        return self is other or hash(self) == hash(other)

    def __hash__(self) -> int:
        return self.hash

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.display_name}\" hash {hash_int_to_str(self.hash)}>"

    def get_referenced_files(self) -> Iterator[int]:
        '''
        Uses the Serializer of this File to find any filse within it.
        '''
        return; yield

    def __copy_empty__(self) -> "AbstractFile[a]":
        '''
        Creates a file with data of the same type as this file, but empty.
        '''
        ...

@Types.register_decorator("file", json_coder=FileCoder)
class File[a](AbstractFile[a]):

    __slots__ = (
        "_data",
        "serializer",
    )

    def __init__(self, display_name:str, serializer:Serializer.Serializer, data_hash:int) -> None:
        super().__init__(display_name, data_hash)
        self.serializer = serializer
        self._data:a|EllipsisType = ...

    def read(self) -> None:
        # installs data without returning anything.
        self.data

    def _get_data(self) -> a:
        if self._data is ...:
            file_bytes = FileStorageManager.read_archived(hash_int_to_str(self.hash))
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

    data = property(_get_data, _set_data, _del_data) # type: ignore

    def __copy_empty__(self) -> AbstractFile[a]:
        return EmptyFile(self.serializer, self.hash, self._data)

    def get_referenced_files(self) -> Iterator[int]:
        if self.serializer.can_contain_subfiles:
            file_bytes = FileStorageManager.read_archived(hash_int_to_str(self.hash))
            yield from self.serializer.get_referenced_files(file_bytes)

@Types.register_decorator(None, json_coder=Types.no_coder)
class EmptyFile[a](File[a]):

    __slots__ = ()

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

    data = property(_get_data, File._set_data, File._del_data) # type: ignore

    def __copy_empty__(self) -> AbstractFile[a]:
        return self

@Types.register_decorator("fake_file")
class FakeFile[a](AbstractFile[a]):
    '''Similar to a File, but it can be created anywhere and using any hash/data.'''

    __slots__ = (
        "data"
    )

    def __init__(self, display_name: str, data:a, data_hash: int) -> None:
        super().__init__(display_name, data_hash)
        self.data = data

    def __copy_empty__(self) -> AbstractFile[a]:
        return FakeFile("empty_file", type(self.data)(), 0) # FakeFile does not need data_hash.
        # the `hash` attribute must be different for caching reasons, so it's just 0.

@Types.register_decorator(None, hashing_method=hash, is_file=True)
class FileDiff[a]():
    '''
    Similar to a FakeFile, but contains the data from multiple files.
    This exists because it's easier to hash or something.
    '''

    __slots__ = (
        "data",
        "display_names",
        "files",
        "hash",
        "last_value",
    )

    def __init__(self, data:a|D.Diff[a], *files:AbstractFile[a]) -> None:
        self.data = data
        self.display_names:list[str] = [file.display_name for file in files]
        self.hash = hash(files)
        self.files = files
        self.last_value = files[-1]

    def __hash__(self) -> int:
        return self.hash

    def __repr__(self) -> str:
        unique_display_names:list[str] = [] # list of display names such that the previous one is not equal to the current one.
        for display_name in self.display_names:
            if len(unique_display_names) == 0 or display_name != unique_display_names[-1]:
                unique_display_names.append(display_name)
        return f"<{self.__class__.__name__} {", ".join(f"\"{display_name}\"" for display_name in unique_display_names)} hash {hash_int_to_str(self.hash)}>"

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
            raise TypeError(f"How do I recursively examine type {data.__class__.__name__} for files?")
