import gzip
from typing import Literal

import Domain.Domain as Domain
from _domains.minecraft_common.scripts.Nbt.DataReader import DataReader
from _domains.minecraft_common.scripts.Nbt.NbtTypes import (
    TAG,
    End,
    parse_compound_item_from_bytes,
)
from Serializer.Serializer import Serializer
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

__all__ = ("NbtSerializer",)

class NbtSerializer(Serializer[TAG]):

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("endianness", True, EnumTypeVerifier([endianness.name.lower() for endianness in End])),
        TypedDictKeyTypeVerifier("gzipped", True, bool),
    )

    def __init__(self, name:str, domain:"Domain.Domain", endianness:Literal["big", "little"], gzipped:bool) -> None:
        '''
        :name: The Component name of this Serializer.
        :endianness: If the content of the nbt file is big-endian or little-endian.
        :gzipped: If True, decompresses the file using gzip.
        '''
        super().__init__(name, domain)
        self.endianness = End[endianness.upper()]
        self.gzipped = gzipped

    def deserialize(self, data: bytes) -> TAG:
        if self.gzipped:
            data = gzip.decompress(data)
        data_reader = DataReader(data)
        return parse_compound_item_from_bytes(data_reader, self.endianness)[1]
