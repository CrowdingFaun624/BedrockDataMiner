from base64 import b64decode

from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer


@component_function()
class ProfanityFilterSerializer(Serializer[list[str]]):

    __slots__ = ()

    def deserialize(self, data: bytes) -> list[str]:
        return b64decode(data).decode().splitlines()
