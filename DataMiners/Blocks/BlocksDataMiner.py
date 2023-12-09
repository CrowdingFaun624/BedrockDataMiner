from typing import Any, TypedDict

import DataMiners.DataMiner as DataMiner

class BlockTypedDict(TypedDict):
    name: str
    defined_in: list[str]
    properties: dict[str,Any]
class ResourcePackTypedDict(TypedDict):
    name: str
    tags: list[str]
    id: int

class BlocksDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data: dict[str,Any]|None=None) -> list[BlockTypedDict]:
        return super().activate(dependency_data)
