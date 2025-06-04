import json
from typing import Any

from Serializer.JsonSerializer import JsonSerializer


class CustomJsonSerializer(JsonSerializer):
    '''
    Serializer for JSON files.
    '''

    can_contain_subfiles = True

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode(), cls=self.domain.json_decoder)
