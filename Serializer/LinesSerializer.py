import Serializer.Serializer as Serializer


class LinesSerializer(Serializer.Serializer[list[str],list[str]]):

    mode = Serializer.Mode.text

    def serialize(self, data: list[str]) -> str:
        return "\n".join(data)

    def deserialize(self, data: str) -> list[str]:
        return data.splitlines()
