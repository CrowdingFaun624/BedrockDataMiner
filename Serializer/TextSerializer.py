from Serializer.Serializer import Serializer


class TextSerializer(Serializer[str]):

    __slots__ = ()

    def deserialize(self, data: bytes) -> str:
        return data.decode()
