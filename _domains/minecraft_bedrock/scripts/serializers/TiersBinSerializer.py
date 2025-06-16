import json
from base64 import b64decode
from typing import Any

from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer


@component_function()
class TiersBinSerializer(Serializer[Any]):

    __slots__ = ()

    def deserialize(self, data: bytes) -> Any:
        return json.loads(b64decode(data.decode()).decode())
