from typing import Any, TypedDict

class BlockTypedDict(TypedDict):
    name: str
    defined_in: list[str]
    properties: dict[str,Any]

class ResourcePackTypedDict(TypedDict):
    name: str
    tags: list[str]
    id: int

class SoundDefinitionSoundTypedDict(TypedDict):
    name: str
    stream: bool
    is3D: bool
    volume: float
    pitch: float
    weight: int
    load_on_low_memory: bool

class SoundDefinitionTypedDict(TypedDict):
    defined_in: list[str]
    category: str
    min_distance: int|float
    max_distance: int|float
    sounds: list[str|SoundDefinitionSoundTypedDict]
    subtitle: str # unused
