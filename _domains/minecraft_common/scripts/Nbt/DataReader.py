import struct
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _domains.minecraft_common.scripts.Nbt.NbtTypes import End


class DataReader():

    def __init__(self, data:bytes) -> None:
        self.data = data
        self.position = 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} pos {self.position}/{len(self.data)}>"

    def read(self, amount:int=1) -> bytes:
        output = self.data[self.position:self.position + amount]
        self.position += amount
        return output

    def unpack(self, format:str, amount:int, endianness:"End") -> tuple[Any,...]:
        format = (endianness.value + format) if endianness is not None else format
        return struct.unpack(format, self.read(amount))

    def unpack_tuple(self, format:str, amount:int, endianness:"End") -> Any:
        format = (endianness.value + format) if endianness is not None else format
        # duplicated because this function is called a zillion times
        # and we don't need the extra function slowing it down.
        return struct.unpack(format, self.read(amount))[0]
