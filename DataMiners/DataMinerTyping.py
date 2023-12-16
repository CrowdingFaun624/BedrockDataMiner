from typing import Any, TypedDict

class BlocksJsonBlockTexturesTypedDict(TypedDict):
    down: str
    east: str
    north: str
    side: str
    south: str
    up: str
    west: str

class BlocksJsonBlockIsotropicTypedDict(TypedDict):
    down: bool
    up: bool

class BlocksJsonBlockTypedDict(TypedDict):
    isotropic: bool|BlocksJsonBlockIsotropicTypedDict
    sound: str
    textures: str|BlocksJsonBlockTexturesTypedDict

class ResourcePackTypedDict(TypedDict):
    brightness_gamma: float
    id: int
    name: str
    tags: list[str]

class SoundDefinitionsJsonSoundTypedDict(TypedDict):
    is3D: bool
    load_on_low_memory: bool
    name: str
    pitch: float
    stream: bool
    volume: float
    weight: int

class SoundDefinitionsJsonSoundEventTypedDict(TypedDict):
    category: str
    defined_in: list[str]
    max_distance: int|float
    min_distance: int|float
    sounds: list[str|SoundDefinitionsJsonSoundTypedDict]
    subtitle: str # unused
