from typing import Any

import pyjson5

from Component.ComponentFunctions import register_builtin
from Serializer.Serializer import Serializer


@register_builtin()
class JsonSerializer(Serializer[Any]):
    '''
    Serializer for JSON files.
    '''

    __slots__ = ()

    def deserialize(self, data: bytes) -> Any:
        return pyjson5.loads(data.decode())
