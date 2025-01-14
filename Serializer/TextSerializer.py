import Serializer.Serializer as Serializer


class TextSerializer(Serializer.Serializer[str,str]):

    def deserialize(self, data: bytes) -> str:
        return data.decode()
