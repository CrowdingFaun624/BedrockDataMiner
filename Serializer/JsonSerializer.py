from typing import Any

import pyjson5

from Serializer.Serializer import Serializer


class JsonSerializer(Serializer[Any]):
    '''
    Serializer for JSON files.
    '''

    def deserialize(self, data: bytes) -> Any:
        return pyjson5.loads(data.decode())
