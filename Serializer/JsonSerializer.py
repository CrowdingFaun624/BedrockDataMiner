from typing import Any

import pyjson5

import Serializer.Serializer as Serializer


class JsonSerializer(Serializer.Serializer[Any, Any]):
    '''
    Serializer for JSON files.
    '''

    def serialize_json(self, data: Any) -> Any:
        return data

    def serialize(self, data: Any) -> bytes:
        return pyjson5.dumps(data).encode()

    def deserialize_json(self, data: Any) -> Any:
        return data

    def deserialize(self, data: bytes) -> Any:
        return pyjson5.loads(data.decode())
