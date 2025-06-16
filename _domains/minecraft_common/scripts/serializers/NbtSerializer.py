import gzip
from typing import Literal

from _domains.minecraft_common.scripts.Nbt.DataReader import DataReader
from _domains.minecraft_common.scripts.Nbt.NbtTypes import (
    TAG,
    End,
    parse_compound_item_from_bytes,
)
from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


@component_function()
class NbtSerializer(Serializer[TAG]):

    __slots__ = (
        "endianness",
        "gzipped",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("endianness", True, EnumTypeVerifier([endianness.name.lower() for endianness in End])),
        TypedDictKeyTypeVerifier("gzipped", True, bool),
    )

    def initialize(self, endianness:Literal["big", "little"], gzipped:bool) -> None:
        '''
        :endianness: If the content of the nbt file is big-endian or little-endian.
        :gzipped: If True, decompresses the file using gzip.
        '''
        self.endianness = End[endianness.upper()]
        self.gzipped = gzipped

    def deserialize(self, data: bytes) -> TAG:
        if self.gzipped:
            data = gzip.decompress(data)
        data_reader = DataReader(data)
        return parse_compound_item_from_bytes(data_reader, self.endianness)[1]
