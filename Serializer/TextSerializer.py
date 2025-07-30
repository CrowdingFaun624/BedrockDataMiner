from Component.ComponentFunctions import register_builtin
from Serializer.Serializer import Serializer


@register_builtin()
class TextSerializer(Serializer[str]):

    __slots__ = ()

    def deserialize(self, data: bytes) -> str:
        return data.decode()
