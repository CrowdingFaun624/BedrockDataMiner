import json
import Serializer.Serializer as Serializer


class TextSerializer(Serializer.Serializer[str,str]):

    def serialize(self, data: str) -> bytes:
        return data.encode()

    def deserialize(self, data: bytes) -> str:
        return data.decode()
