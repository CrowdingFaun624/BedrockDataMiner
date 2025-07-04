import json
from pathlib import Path
from types import EllipsisType

import Utilities.Exceptions as Exceptions
from Utilities.FileManager import PARENT_DIRECTORY


class Cache[T]():
    '''
    Class that stores data from a file. Does not read the file until it is
    first accessed. Must be overridden.
    '''

    can_be_written:bool = True

    __slots__ = (
        "data",
        "has_opened",
        "path",
    )

    def __init__(self, path:Path) -> None:
        self.path = path
        self.has_opened = False
        self.data:T|EllipsisType = ...

    def get_default_content(self) -> T|None:
        '''
        If the file does not exist, this method is called.
        If it returns None, then an exception is raised.
        '''
        ...

    def read(self) -> bytes:
        '''
        Reads the file into bytes. Should not be overridden.
        '''
        with open(self.path, "rb") as f:
            return f.read()

    def deserialize(self, data:bytes) -> T:
        '''
        Deserializes the bytes of the file into the data format.
        '''
        ...

    def serialize(self, data:T) -> bytes:
        '''
        Sserializes the data format into bytes of the file.
        '''
        ...

    def forget(self) -> None:
        '''
        Sets this Cache back to its unopened state, so that its contents can be
        removed from memory.
        '''
        self.has_opened = False
        self.data = ...

    def get(self) -> T:
        '''
        Opens the Cache. Should not be overridden.
        '''
        if not self.has_opened:
            self.has_opened = True
            if self.path.exists():
                self.data = self.deserialize(self.read())
            else:
                default_content = self.get_default_content()
                if default_content is None:
                    raise Exceptions.CacheFileNotFoundError(self)
                self.data = default_content
        assert self.data is not ...
        return self.data

    def write(self, value:T|None=None) -> None:
        '''
        Overwrites the Cache's file. Can only be called if `deserialize`
        is overridden. Should not be overridden. If `value` is None, only
        write to the file without changing the data.
        '''
        if not self.can_be_written:
            raise Exceptions.CacheCannotWriteError(self)
        if self.data is ...:
            self.has_opened = True
        if value is not None:
            self.data = value
        deserialized_data = self.serialize(self.get())
        if deserialized_data is None:
            raise Exceptions.CacheDeserializeError(self)
        else:
            with open(self.path, "wb") as f:
                f.write(deserialized_data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {"open" if self.has_opened else "unopened"} {self.path.relative_to(PARENT_DIRECTORY).as_posix()}>"

class JsonCache[T](Cache[T]):

    __slots__ = ()

    decoder:type[json.JSONDecoder] = json.JSONDecoder

    encoder:type[json.JSONEncoder] = json.JSONEncoder

    def deserialize(self, data: bytes) -> T:
        return json.loads(data, cls=self.decoder)

    def serialize(self, data: T) -> bytes:
        return json.dumps(data, cls=self.encoder).encode("UTF8")

class LinesCache[T, W](Cache[T]):

    __slots__ = ()

    def serialize_line(self, data:W) -> str:
        '''
        Serializes the data format into a string that can be appended to the
        file.
        '''
        ...

    def append_new_line(self, data:W) -> None:
        '''
        Changes the `data` attribute of this Cache (what is returned by the
        `get` method) to include the `data` parameter of this method.
        '''
        ...

    def write_new_line(self, data:W) -> None:
        '''
        Adds a new line of data to this Cache. Should not be overridden.
        '''
        self.append_new_line(data)
        deserialized_data = self.serialize_line(data)
        if deserialized_data is None:
            raise Exceptions.CacheDeserializeError(self, "(in write_new_line)")
        else:
            with open(self.path, "at") as f:
                f.write(deserialized_data)
