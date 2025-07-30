import json
from typing import Any

from Component.ComponentFunctions import register_builtin
from Serializer.JsonSerializer import JsonSerializer


@register_builtin()
class CustomJsonSerializer(JsonSerializer):
    '''
    Serializer for JSON files.
    '''

    __slots__ = ()

    can_contain_subfiles = True

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode(), cls=self.domain.json_decoder)
