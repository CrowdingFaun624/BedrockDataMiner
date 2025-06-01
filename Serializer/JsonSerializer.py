from typing import Any

import pyjson5

import Serializer.Serializer as Serializer


class JsonSerializer(Serializer.Serializer[Any]):
    '''
    Serializer for JSON files.
    '''

    def deserialize(self, data: bytes) -> Any:
        return pyjson5.loads(data.decode())
