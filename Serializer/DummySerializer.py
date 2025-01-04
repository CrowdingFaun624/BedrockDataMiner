import Domain.Domain as Domain
import Serializer.Serializer as Serializer
import Utilities.TypeVerifier as TypeVerifier


class DummySerializer(Serializer.Serializer):

    store_as_file_default = True

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("empty_okay", "a bool", False, bool),
    )

    def __init__(self, name: str, domain:"Domain.Domain", empty_okay:bool=False) -> None:
        super().__init__(name, domain)
        self.empty_okay = empty_okay

    def deserialize(self, data: bytes) -> None:
        return None
