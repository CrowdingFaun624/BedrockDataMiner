import Domain.Domain as Domain
from Serializer.Serializer import Serializer
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class DummySerializer(Serializer):

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("empty_okay", False, bool),
    )

    def __init__(self, name: str, domain:"Domain.Domain", empty_okay:bool=False) -> None:
        super().__init__(name, domain)
        self.empty_okay = empty_okay

    def deserialize(self, data: bytes) -> None:
        return None
