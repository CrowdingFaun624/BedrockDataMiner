from typing import TypedDict

import Serializer.Serializer as Serializer

__all__ = ["GlyphSizesSerializer"]

class RangeTypedDict(TypedDict):
    left: int
    right: int

class GlyphSizesSerializer(Serializer.Serializer[dict[str,RangeTypedDict], dict[str,RangeTypedDict]]):
    
    def deserialize(self, data: bytes) -> dict[str,RangeTypedDict]:
        output:dict[str,RangeTypedDict] = {}
        for index, byte in enumerate(bytearray(data)):
            left_end = byte & 0x0F
            right_end = byte & 0xF0 >> 4
            assert right_end >= left_end
            character = bytes(index).decode()
            output[character] = {"left": left_end, "right": right_end}
        return output
            
