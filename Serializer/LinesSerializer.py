from Serializer.Serializer import Serializer


class LinesSerializer(Serializer[list[str]]):

    def deserialize(self, data: bytes) -> list[str]:
        return data.decode().splitlines()
