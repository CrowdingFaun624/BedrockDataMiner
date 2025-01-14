import gzip
from typing import Literal

import _domains.minecraft_common.scripts.Nbt.DataReader as DataReader
import _domains.minecraft_common.scripts.Nbt.NbtTypes as NbtTypes
import Domain.Domain as Domain
import Serializer.Serializer as Serializer
import Utilities.TypeVerifier as TypeVerifier

__all__ = ["NbtSerializer"]

class NbtSerializer(Serializer.Serializer[NbtTypes.TAG, None]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", True, TypeVerifier.EnumTypeVerifier([endianness.name.lower() for endianness in NbtTypes.End])),
        TypeVerifier.TypedDictKeyTypeVerifier("gzipped", "a bool", True, bool),
    )

    store_as_file_default = True

    def __init__(self, name:str, domain:"Domain.Domain", endianness:Literal["big", "little"], gzipped:bool) -> None:
        '''
        :name: The Component name of this Serializer.
        :endianness: If the content of the nbt file is big-endian or little-endian.
        :gzipped: If True, decompresses the file using gzip.
        '''
        super().__init__(name, domain)
        self.endianness = NbtTypes.End[endianness.upper()]
        self.gzipped = gzipped

    def deserialize(self, data: bytes) -> NbtTypes.TAG:
        if self.gzipped:
            data = gzip.decompress(data)
        data_reader = DataReader.DataReader(data)
        return NbtTypes.parse_compound_item_from_bytes(data_reader, self.endianness)[1]
