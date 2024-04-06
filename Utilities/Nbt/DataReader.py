import struct
from typing import Any, BinaryIO

import Utilities.Nbt.Endianness as Endianness

class DataReader():
    def read(self, amount:int=1) -> bytes: ...
    def unpack(self, format:str, amount:int, endianness:Endianness.End) -> tuple[Any,...]:
        format = (endianness.value + format) if endianness is not None else format
        return struct.unpack(format, self.read(amount))
    def unpack_tuple(self, format:str, amount:int, endianness:Endianness.End) -> Any:
        return self.unpack(format, amount, endianness)[0]

class DataBytesReader(DataReader):
    def __init__(self, data:bytes) -> None:
        self.data = data
        self.position = 0
    def read(self, amount:int=1) -> bytes:
        output = self.data[self.position:self.position + amount]
        self.position += amount
        return output

class DataFileReader(DataReader):
    def __init__(self, file:BinaryIO) -> None:
        self.data = file
    def read(self, amount:int=1) -> bytes:
        return self.data.read(amount)
    def __exit__(self, exception_type, exception_value, traceback) -> None:
        print(exception_type, exception_value, traceback)
        self.data.close()
    def __enter__(self) -> "DataFileReader":
        return self
