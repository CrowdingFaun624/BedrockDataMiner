import json
from typing import Any, Iterator

import Serializer.JsonSerializer as JsonSerializer
import Utilities.File as File


class CustomJsonSerializer(JsonSerializer.JsonSerializer):
    '''
    Serializer for JSON files.
    '''

    can_contain_subfiles = True

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode(), cls=self.domain.json_decoder)

    def get_referenced_files(self, data: bytes) -> Iterator[int]:
        yield from File.recursive_examine_data_for_files(self.deserialize(data))
