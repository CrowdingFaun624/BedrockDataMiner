from typing import Any, TypedDict

import Comparison.Difference as D
import Comparison.Compare as Compare

class DependenciesTypedDict(TypedDict):
    behavior_packs: "BehaviorPacks"
    blocks: "MyBlocksClient"
    duplicate_sounds: "DuplicateSounds"
    entities: "Entities"
    items: "Items"
    languages: "Languages"
    music_definitions: "MyMusicDefinitions"
    non_existent_sounds: "NonExistentSounds"
    recipes: "Recipes"
    resource_packs: "ResourcePacks"
    sound_definitions: "MySoundDefinitionsJson"
    sound_files: "SoundFiles"
    sounds_json: "MySoundsJson"
    undefined_sound_events: "UndefinedSoundEvents"
    unused_sound_events: "UnusedSoundEvents"

# behavior packs

class BehaviorPackTypedDict(TypedDict):
    id: int
    name: str
    tags: list[str]

BehaviorPacks = list[BehaviorPackTypedDict]

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

class BlocksJsonClientBlockTypedDict(TypedDict):
    blockshape: str
    brightness_gamma: float
    carried_textures: str|BlocksJsonBlockTexturesTypedDict
    isotropic: bool|BlocksJsonBlockIsotropicTypedDict
    sound: str
    textures: str|BlocksJsonBlockTexturesTypedDict

class MyBlocksJsonClientBlockTypedDict(TypedDict):
    name: str
    properties: BlocksJsonClientBlockTypedDict

class DiffBlocksJsonClientBlockTexturesTypedDict(TypedDict):
    down: str|D.Diff[str,str]
    east: str|D.Diff[str,str]
    north: str|D.Diff[str,str]
    side: str|D.Diff[str,str]
    south: str|D.Diff[str,str]
    up: str|D.Diff[str,str]
    west: str|D.Diff[str,str]

class DiffBlocksJsonClientBlockIsotropicTypedDict(TypedDict):
    down: bool|D.Diff[bool,bool]
    up: bool|D.Diff[bool,bool]

class DiffBlocksJsonClientBlockTypedDict(TypedDict):
    blockshape: str|D.Diff[str,str]
    brightness_gamma: float|D.Diff[float,float]
    carried_textures: str|DiffBlocksJsonClientBlockTexturesTypedDict|D.Diff[str|DiffBlocksJsonClientBlockTexturesTypedDict,str|DiffBlocksJsonClientBlockTexturesTypedDict]
    defined_in: list[str|D.Diff[str,str]]
    isotropic: bool|DiffBlocksJsonClientBlockIsotropicTypedDict|D.Diff[bool|DiffBlocksJsonClientBlockIsotropicTypedDict,bool|DiffBlocksJsonClientBlockIsotropicTypedDict]
    sound: str|D.Diff[str,str]
    textures: str|DiffBlocksJsonClientBlockTexturesTypedDict|D.Diff[str|DiffBlocksJsonClientBlockTexturesTypedDict,str|DiffBlocksJsonClientBlockTexturesTypedDict]

class NormalizedBlocksJsonClientBlockTypedDict(TypedDict):
    blockshape: str
    brightness_gamma: float
    carried_textures: str|BlocksJsonBlockTexturesTypedDict
    defined_in: list[str]
    isotropic: bool|BlocksJsonBlockIsotropicTypedDict
    sound: str
    textures: str|BlocksJsonBlockTexturesTypedDict

BlocksClient = dict[str,BlocksJsonClientBlockTypedDict]
MyBlocksClient = list[MyBlocksJsonClientBlockTypedDict]
NormalizedBlocksClient = dict[str,dict[str,NormalizedBlocksJsonClientBlockTypedDict]]
DiffBlocksClient = dict[str|D.Diff[str,str],dict[str|D.Diff[str,str],DiffBlocksJsonClientBlockTypedDict|D.Diff[DiffBlocksJsonClientBlockTypedDict,DiffBlocksJsonClientBlockTypedDict]]]

# duplicate sounds

class DuplicateSoundsTypedDict(TypedDict):
    file_name: str
    file_internal_name: str

DuplicateSounds = dict[str,list[DuplicateSoundsTypedDict]]
NormalizedDuplicateSounds = dict[str,list[DuplicateSoundsTypedDict]]

# entities

Entities = dict[str,dict[str,Any]] # TODO: fill this out

# items

Items = dict[str,dict[str,Any]] # TODO: fill this out

# languages

class LanguagesPropertiesTypedDict(TypedDict):
    name: str

class LanguagesTypedDict(TypedDict):
    code: str
    defined_in: list[str]
    properties: dict[str,LanguagesPropertiesTypedDict]

Languages = list[LanguagesTypedDict]
NormalizedLanguages = dict[str,dict[str,LanguagesPropertiesTypedDict]]

# music_definitions.json

class MusicDefinitionsEnvironmentTypedDict(TypedDict):
    event_name: str
    min_delay: int
    max_delay: int

MusicDefinitions = dict[str,MusicDefinitionsEnvironmentTypedDict]
MyMusicDefinitions = dict[str,dict[str,MusicDefinitionsEnvironmentTypedDict]]

# non-existent sounds

NonExistentSounds = dict[str,dict[str,list[str]]]
NormalizedNonExistentSounds = dict[str,dict[str,set[str]]]

# recipes

Recipes = dict[str,dict[str,Any]] # TODO: fill this out

# resource packs

class ResourcePackTypedDict(TypedDict):
    id: int
    name: str
    tags: list[str]

ResourcePacks = list[ResourcePackTypedDict]

# sound_definitions.json

class SoundDefinitionsJsonSoundTypedDict(TypedDict):
    exclude_from_pocket_platforms: bool
    is3D: bool
    load_on_low_memory: bool
    name: str
    pitch: float
    stream: bool
    type: str
    volume: float
    weight: int

class NormalizedSoundDefinitionsJsonSoundTypedDict(TypedDict):
    exclude_from_pocket_platforms: bool
    is3D: bool
    load_on_low_memory: bool
    pitch: float
    stream: bool
    type: str
    volume: float
    weight: int

class SoundDefinitionsJsonSoundEventTypedDict(TypedDict):
    category: str
    max_distance: int|float
    min_distance: int|float
    sounds: list[str|SoundDefinitionsJsonSoundTypedDict]
    subtitle: str # unused

class NormalizedSoundDefinitionsJsonSoundEventTypedDict(TypedDict):
    category: str
    defined_in: list[str]
    max_distance: int|float
    min_distance: int|float
    sounds: dict[str,SoundDefinitionsJsonSoundTypedDict]
    subtitle: str # unused

SoundDefinitionsJson = dict[str,SoundDefinitionsJsonSoundEventTypedDict]
MySoundDefinitionsJson = dict[str,dict[str,SoundDefinitionsJsonSoundEventTypedDict]]
NormalizedSoundDefinitionsJson = dict[str,dict[str,NormalizedSoundDefinitionsJsonSoundEventTypedDict]]

# sound files

class SoundFilesTagsTypedDict(TypedDict):
    comment: list[str]
    title: list[str]
    tracknumber: list[str]

class SoundFilesStreamInfoTypedDict(TypedDict):
    _start: int
    _size: int
    _version: list[int]
    _extension_data: None
    audio_format: str
    bit_depth: int
    bitrate: float|int
    channels: int
    duration: float
    max_bitrate: int
    min_bitrate: int
    nominal_bitrate: int
    sample_rate: int

class SoundFilesTypedDict(TypedDict):
    filesize: int
    pictures: list
    tags: SoundFilesTagsTypedDict
    _subchunks: list
    _obj: str
    streaminfo: SoundFilesStreamInfoTypedDict
    sha1_hash: str # hexadecimal 40-digit string

class NormalizedSoundFilesTypedDict(TypedDict):
    filesize: int
    pictures: list
    tags: SoundFilesTagsTypedDict
    streaminfo: SoundFilesStreamInfoTypedDict
    sha1_hash: str # hexadecimal 40-digit string

SoundFiles=dict[str,dict[str,SoundFilesTypedDict]]
NormalizedSoundFiles=dict[str,dict[str,NormalizedSoundFilesTypedDict]]

# sounds.json

class SoundsJsonSoundTypedDict(TypedDict):
    sound:str
    sounds: str
    volume: float|int|list[float|int,float|int]
    pitch: float|int|list[float|int,float|int]

class SoundsJsonSoundCollectionTypedDict(TypedDict):
    volume: float|list[float,float]
    pitch: float|list[float,float]
    events:dict[str, str|SoundsJsonSoundTypedDict]|dict[str,dict[str,str]]

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
    events: dict[str, dict[str, SoundsJsonSoundTypedDict]]|dict[str,dict[str,dict[str,str]]]

class ResourcePackSoundsJsonSoundCollectionTypedDict(TypedDict):
    volume: dict[str, float|list[float, float]]
    pitch: dict[str, float|list[float, float]]
    events: dict[str, dict[str, SoundsJsonSoundTypedDict]]|dict[str,dict[str,dict[str,str]]]

class MySoundsJsonTypedDict(TypedDict):
    individual_event_sounds: ResourcePackSoundsJsonFlatCollectionTypedDict
    block_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]
    interactive_block_sounds: dict[str, ResourcePackSoundsJsonFlatCollectionTypedDict]
    entity_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]
    interactive_entity_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]

MySoundsJson = MySoundsJsonTypedDict

# undefined_sound_events

UndefinedSoundEvents = dict[str,list[list[str]]] # TODO: fill this out

# unused_sound_events

UnusedSoundEvents = list[str]
