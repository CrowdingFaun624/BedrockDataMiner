import json
from base64 import b64decode
from typing import Any

from Serializer.Serializer import Serializer

__all__ = ("TiersBinSerializer",)

class TiersBinSerializer(Serializer[Any]):

    __slots__ = ()

    def deserialize(self, data: bytes) -> Any:
        return json.loads(b64decode(data.decode()).decode())
