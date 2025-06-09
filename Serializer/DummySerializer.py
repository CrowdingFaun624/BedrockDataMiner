from Serializer.Serializer import Serializer
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class DummySerializer(Serializer):

    __slots__ = (
        "empty_okay",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("empty_okay", False, bool),
    )

    def initialize(self, empty_okay:bool=False) -> None:
        self.empty_okay = empty_okay

    def deserialize(self, data: bytes) -> None:
        return None
