from typing import TypedDict

import Comparison.Difference as D
import Comparison.Compare as Compare

class DependenciesTypedDict(TypedDict):
    blocks: "MyBlocks"
    duplicate_sounds: "DuplicateSounds"
    languages: "Languages"
    non_existent_sounds: "NonExistentSounds"
    resource_packs: "ResourcePacks"
    sound_definitions: "MySoundDefinitionsJson"
    sound_files: "SoundFiles"
    sounds_json: "MySoundsJson"

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
    blockshape: str
    brightness_gamma: float
    carried_textures: str|BlocksJsonBlockTexturesTypedDict
    isotropic: bool|BlocksJsonBlockIsotropicTypedDict
    sound: str
    textures: str|BlocksJsonBlockTexturesTypedDict

class MyBlocksJsonBlockTypedDict(TypedDict):
    name: str
    properties: BlocksJsonBlockTypedDict

class DiffBlocksJsonBlockTexturesTypedDict(TypedDict):
    down: str|D.Diff[str,str]
    east: str|D.Diff[str,str]
    north: str|D.Diff[str,str]
    side: str|D.Diff[str,str]
    south: str|D.Diff[str,str]
    up: str|D.Diff[str,str]
    west: str|D.Diff[str,str]

class DiffBlocksJsonBlockIsotropicTypedDict(TypedDict):
    down: bool|D.Diff[bool,bool]
    up: bool|D.Diff[bool,bool]

class DiffBlocksJsonBlockTypedDict(TypedDict):
    blockshape: str|D.Diff[str,str]
    brightness_gamma: float|D.Diff[float,float]
    carried_textures: str|DiffBlocksJsonBlockTexturesTypedDict|D.Diff[str|DiffBlocksJsonBlockTexturesTypedDict,str|DiffBlocksJsonBlockTexturesTypedDict]
    defined_in: list[str|D.Diff[str,str]]
    isotropic: bool|DiffBlocksJsonBlockIsotropicTypedDict|D.Diff[bool|DiffBlocksJsonBlockIsotropicTypedDict,bool|DiffBlocksJsonBlockIsotropicTypedDict]
    sound: str|D.Diff[str,str]
    textures: str|DiffBlocksJsonBlockTexturesTypedDict|D.Diff[str|DiffBlocksJsonBlockTexturesTypedDict,str|DiffBlocksJsonBlockTexturesTypedDict]

class NormalizedBlocksJsonBlockTypedDict(TypedDict):
    blockshape: str
    brightness_gamma: float
    carried_textures: str|BlocksJsonBlockTexturesTypedDict
    defined_in: list[str]
    isotropic: bool|BlocksJsonBlockIsotropicTypedDict
    sound: str
    textures: str|BlocksJsonBlockTexturesTypedDict

Blocks = dict[str,BlocksJsonBlockTypedDict]
MyBlocks = list[MyBlocksJsonBlockTypedDict]
NormalizedBlocks = dict[str,dict[str,DiffBlocksJsonBlockTypedDict]]
DiffBlocks = dict[str|D.Diff[str,str],dict[str|D.Diff[str,str],DiffBlocksJsonBlockTypedDict|D.Diff[DiffBlocksJsonBlockTypedDict,DiffBlocksJsonBlockTypedDict]]]

# duplicate sounds

class DuplicateSoundsTypedDict(TypedDict):
    file_name: str
    file_internal_name: str

DuplicateSounds = dict[str,list[DuplicateSoundsTypedDict]]
NormalizedDuplicateSounds = dict[str,Compare.UnorderedList[DuplicateSoundsTypedDict]]

# languages

class LanguagesPropertiesTypedDict(TypedDict):
    name: str

class LanguagesTypedDict(TypedDict):
    code: str
    defined_in: list[str]
    properties: dict[str,LanguagesPropertiesTypedDict]

Languages = list[LanguagesTypedDict]
NormalizedLanguages = dict[str,dict[str,LanguagesPropertiesTypedDict]]

# non-existent sounds

NonExistentSounds = dict[str,dict[str,list[str]]]
NormalizedNonExistentSounds = dict[str,dict[str,set[str]]]

# resource packs

class ResourcePackTypedDict(TypedDict):
    id: int
    name: str
    tags: list[str]

ResourcePacks = list["ResourcePackTypedDict"]

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

class SoundDefinitionsJsonSoundEventTypedDict(TypedDict):
    category: str
    max_distance: int|float
    min_distance: int|float
    sounds: list[str|SoundDefinitionsJsonSoundTypedDict]
    subtitle: str # unused

class NormalizedSoundDefinitionsJsonSoundEventTypedDict(TypedDict):
    category: str
    max_distance: int|float
    min_distance: int|float
    sounds: list[str|SoundDefinitionsJsonSoundTypedDict]
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
    sounds: str
    volume: float|int|list[float|int,float|int]
    pitch: float|int|list[float|int,float|int]

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

MySoundsJson = MySoundsJsonTypedDict
