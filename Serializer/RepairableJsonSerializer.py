from typing import Any

import Serializer.JsonSerializer as JsonSerializer
import Serializer.Serializer as Serializer
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class RepairableJsonSerializer(JsonSerializer.JsonSerializer):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("append", "a str", True, str),
    )

    mode = Serializer.Mode.text

    def __init__(self, append:str) -> None:
        super().__init__()
        self.repair_function = lambda data: data + append

    def deserialize(self, data: str) -> Any:
        return super().deserialize(self.repair_function(data))
