import json
from typing import Any

import Serializer.JsonSerializer as JsonSerializer


class CustomJsonSerializer(JsonSerializer.JsonSerializer):
    '''
    Serializer for JSON files.
    '''

    can_contain_subfiles = True

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode(), cls=self.domain.json_decoder)
