from typing import NotRequired, TypedDict

from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer


class RangeTypedDict(TypedDict):
    character: NotRequired[str]
    left: int
    right: int

@component_function()
class GlyphSizesSerializer(Serializer[dict[str,RangeTypedDict]]):

    __slots__ = ()

    def deserialize(self, data: bytes) -> dict[str,RangeTypedDict]:
        output:dict[str,RangeTypedDict] = {}
        for index, byte in enumerate(bytearray(data)):
            left_end = byte & 0x0F
            right_end = byte & 0xF0 >> 4
            assert right_end >= left_end
            character = chr(index)
            try:
                character.encode("UTF8")
            except UnicodeEncodeError:
                character = None
            character_dict:RangeTypedDict = {"left": left_end, "right": right_end}
            if character is not None:
                character_dict["character"] = character
            output[hex(index)[2:].upper().zfill(4)] = character_dict
        return output
