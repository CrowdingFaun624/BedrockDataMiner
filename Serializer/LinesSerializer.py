import Serializer.Serializer as Serializer


class LinesSerializer(Serializer.Serializer[list[str],list[str]]):

    def deserialize(self, data: bytes) -> list[str]:
        return data.decode().splitlines()
