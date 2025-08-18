import json

from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer


@component_function()
class TextureListSerializer(Serializer):
    """
    I have made a situation in which two different formats must
    be squeezed into the same Serializer. oops.
    """

    __slots__ = ()

    def deserialize(self, data: bytes) -> list[str]:
        data_str = data.decode()
        if data_str[0] == "[":
            return json.loads(data_str)
        else:
            return data_str.splitlines()
