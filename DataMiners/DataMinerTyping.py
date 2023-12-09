from typing import Any, TypedDict

class BlockTypedDict(TypedDict):
    name: str
    defined_in: list[str]
    properties: dict[str,Any]

class ResourcePackTypedDict(TypedDict):
    name: str
    tags: list[str]
    id: int
