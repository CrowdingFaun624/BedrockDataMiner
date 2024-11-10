import json
from typing import Any, Iterator

import Serializer.JsonSerializer as JsonSerializer
import Utilities.CustomJson as CustomJson
import Utilities.File as File


class CustomJsonSerializer(JsonSerializer.JsonSerializer):
    '''
    Serializer for JSON files.
    '''

    can_contain_subfiles = True

    def serialize_json(self, data: Any) -> Any:
        return data

    def serialize(self, data: Any) -> bytes:
        return json.dumps(data, cls=CustomJson.encoder).encode()

    def deserialize_json(self, data: Any) -> Any:
        return data

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode(), cls=CustomJson.decoder)

    def get_referenced_files(self, data: bytes) -> Iterator[int]:
        yield from File.recursive_examine_data_for_files(self.deserialize(data))
