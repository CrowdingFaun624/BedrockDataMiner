from base64 import b64decode

from Serializer.Serializer import Serializer

__all__ = ("ProfanityFilterSerializer",)

class ProfanityFilterSerializer(Serializer[list[str]]):

    __slots__ = ()

    def deserialize(self, data: bytes) -> list[str]:
        return b64decode(data).decode().splitlines()
