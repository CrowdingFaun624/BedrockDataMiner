from typing import Any

import pyjson5

from Serializer.Serializer import Serializer


class JsonSerializer(Serializer[Any]):
    '''
    Serializer for JSON files.
    '''

    __slots__ = ()

    def deserialize(self, data: bytes) -> Any:
        return pyjson5.loads(data.decode())
