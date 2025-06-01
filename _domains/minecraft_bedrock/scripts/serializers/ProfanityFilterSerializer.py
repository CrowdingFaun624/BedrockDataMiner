import base64

import Serializer.Serializer as Serializer

__all__ = ("ProfanityFilterSerializer",)

class ProfanityFilterSerializer(Serializer.Serializer[list[str]]):

    def deserialize(self, data: bytes) -> list[str]:
        return base64.b64decode(data).decode().splitlines()
