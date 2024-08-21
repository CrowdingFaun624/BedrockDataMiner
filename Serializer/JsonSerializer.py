from typing import Any

import pyjson5

import Serializer.Serializer as Serializer


class JsonSerializer(Serializer.Serializer[Any, Any]):
    '''
    Serializer for JSON files.
    '''

    mode = Serializer.Mode.text

    def serialize_json(self, data: Any) -> Any:
        return data

    def serialize(self, data: Any) -> str:
        return pyjson5.dumps(data)

    def deserialize_json(self, data: Any) -> Any:
        return data

    def deserialize(self, data: str) -> Any:
        return pyjson5.loads(data)
