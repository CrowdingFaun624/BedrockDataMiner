from typing import Any

from Serializer.Serializer import Serializer
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class LinesSerializer(Serializer[list[str]]):

    __slots__ = (
        "encoding",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("encoding", False, str),
    )

    def initialize(self, encoding:str="utf-8") -> None:
        self.encoding = encoding

    def deserialize(self, data: bytes) -> list[str]:
        return data.decode(self.encoding).splitlines()
