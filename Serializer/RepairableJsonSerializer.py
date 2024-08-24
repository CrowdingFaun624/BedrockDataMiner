from typing import Any, Callable

import Serializer.JsonSerializer as JsonSerializer
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class RepairableJsonSerializer(JsonSerializer.JsonSerializer):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("remove_suffix", "a str", True, str),
    )

    def __init__(self, name:str, remove_suffix:str) -> None:
        super().__init__(name)
        remove_suffix_bytes = remove_suffix.encode()
        self.repair_function:Callable[[bytes],bytes] = lambda data: data.removesuffix(remove_suffix_bytes)

    def deserialize(self, data: bytes) -> Any:
        return super().deserialize(self.repair_function(data))
