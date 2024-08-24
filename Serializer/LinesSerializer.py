import Serializer.Serializer as Serializer


class LinesSerializer(Serializer.Serializer[list[str],list[str]]):

    def serialize(self, data: list[str]) -> str:
        return "\n".join(data)

    def deserialize(self, data: bytes) -> list[str]:
        return data.decode().splitlines()
