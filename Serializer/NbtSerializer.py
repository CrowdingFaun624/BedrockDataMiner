from typing import Literal

import Serializer.Serializer as Serializer
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
from Utilities.Nbt.Endianness import End


class NbtSerializer(Serializer.Serializer[NbtTypes.TAG, None]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", True, TypeVerifier.EnumTypeVerifier([endianness.name.lower() for endianness in End])),
        TypeVerifier.TypedDictKeyTypeVerifier("gzipped", "a bool", True, bool),
    )

    store_as_file_default = True

    def __init__(self, name:str, endianness:Literal["big", "little"], gzipped:bool) -> None:
        '''
        :name: The Component name of this Serializer.
        :endianness: If the content of the nbt file is big-endian or little-endian.
        :gzipped: If True, decompresses the file using gzip.
        '''
        super().__init__(name)
        self.endianness = End[endianness.upper()]
        self.gzipped = gzipped

    def deserialize(self, data: bytes) -> NbtTypes.TAG:
        return NbtReader.unpack_bytes(data, gzipped=self.gzipped, endianness=self.endianness)[1]