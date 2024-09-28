from typing import Any, Callable

import Serializer.JsonSerializer as JsonSerializer
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class RepairableJsonSerializer(JsonSerializer.JsonSerializer):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("replace_suffix_old", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("replace_suffix_new", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_suffix", "a str", False, str),
        function=lambda data: (("replace_suffix_old" in data) == ("replace_suffix_new" in data), "key \"replace_suffix_old\" requires \"replace_suffix_new\" and vice versa")
    )

    def __init__(self, name:str, remove_suffix:str|None=None, replace_suffix_old:str|None=None, replace_suffix_new:str|None=None) -> None:
        super().__init__(name)
        if remove_suffix is not None:
            # removes suffix if it exists
            remove_suffix_bytes = remove_suffix.encode()
            self.repair_function:Callable[[bytes],bytes] = lambda data: data.removesuffix(remove_suffix_bytes)
        elif replace_suffix_old is not None:
            # replaces old suffix with new suffix if it exists
            assert replace_suffix_new is not None
            replace_suffix_old_bytes = replace_suffix_old.encode()
            replace_suffix_new_bytes = replace_suffix_new.encode()
            self.repair_function = lambda data: data if not data.endswith(replace_suffix_old_bytes) else data.removesuffix(replace_suffix_old_bytes) + replace_suffix_new_bytes

    def deserialize(self, data: bytes) -> Any:
        return super().deserialize(self.repair_function(data))
