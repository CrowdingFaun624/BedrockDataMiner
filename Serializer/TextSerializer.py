from Serializer.Serializer import Serializer


class TextSerializer(Serializer[str]):

    def deserialize(self, data: bytes) -> str:
        return data.decode()
