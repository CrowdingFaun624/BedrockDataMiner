from typing import Any

import pyjson5

from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer


@component_function()
class PackMcmetaSerializer(Serializer):

    def deserialize(self, data: bytes) -> Any:
        if data.startswith(b"T"):
            return {"pack": {"description": data.decode()}}
        else:
            return pyjson5.loads(data.decode())
