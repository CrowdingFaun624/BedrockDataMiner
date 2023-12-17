from typing import TypedDict

class DependenciesTypedDict(TypedDict):
    blocks: dict[str,dict[str,"BlocksJsonBlockTypedDict"]]
    resource_packs: list["ResourcePackTypedDict"]
    sound_definitions: dict[str,dict[str,"SoundDefinitionsJsonSoundEventTypedDict"]]
    sounds_json: "MySoundsJsonTypedDict"

# blocks.json

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
    brightness_gamma: float
    isotropic: bool|BlocksJsonBlockIsotropicTypedDict
    sound: str
    textures: str|BlocksJsonBlockTexturesTypedDict

# resource packs

class ResourcePackTypedDict(TypedDict):
    id: int
    name: str
    tags: list[str]

# sound_definitions.json

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

# sounds.json

class SoundsJsonSoundTypedDict(TypedDict):
    sounds: str
    volume: float|list[float,float]
    pitch: float|list[float,float]

class SoundsJsonSoundCollectionTypedDict(TypedDict):
    volume: float|list[float,float]
    pitch: float|list[float,float]
    events:dict[str, str|SoundsJsonSoundTypedDict]

class SoundsJsonFlatCollectionTypedDict(TypedDict): # "flat" means that it doesn't have volume or pitch defined right here.
    events: dict[str, SoundsJsonSoundTypedDict]

class SoundsJsonEntitySoundsTypedDict(TypedDict):
    defaults: SoundsJsonSoundCollectionTypedDict
    entities: dict[str, SoundsJsonSoundCollectionTypedDict]

class SoundsJsonInteractiveSoundsTypedDict(TypedDict):
    block_sounds: dict[str, SoundsJsonSoundCollectionTypedDict]
    entity_sounds: SoundsJsonEntitySoundsTypedDict

class SoundsJsonTypedDict(TypedDict):
    individual_event_sounds: SoundsJsonFlatCollectionTypedDict
    block_sounds: dict[str, SoundsJsonSoundCollectionTypedDict]
    entity_sounds: SoundsJsonEntitySoundsTypedDict
    interactive_sounds: SoundsJsonInteractiveSoundsTypedDict

class ResourcePackSoundsJsonFlatCollectionTypedDict(TypedDict):
    events: dict[str, dict[str, SoundsJsonSoundTypedDict]]

class ResourcePackSoundsJsonSoundCollectionTypedDict(TypedDict):
    volume: dict[str, float|list[float, float]]
    pitch: dict[str, float|list[float, float]]
    events: dict[str, dict[str, SoundsJsonSoundTypedDict]]

class MySoundsJsonTypedDict(TypedDict):
    individual_event_sounds: ResourcePackSoundsJsonFlatCollectionTypedDict
    block_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]
    interactive_block_sounds: dict[str, ResourcePackSoundsJsonFlatCollectionTypedDict]
    entity_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]
    interactive_entity_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]
