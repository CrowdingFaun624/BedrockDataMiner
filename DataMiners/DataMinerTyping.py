from typing import Any, Literal, TypedDict

from typing_extensions import NotRequired, Required

DependenciesLiterals = Literal["behavior_packs", "blocks", "credits", "duplicate_sounds", "entities", "entities_client", "items", "language", "languages", "loading_tips", "loot_tables", "models", "music_definitions", "non_existent_sounds", "recipes", "resource_packs", "sound_definitions", "sound_files", "sounds_json", "splashes", "trade_tables", "undefined_sound_events", "unused_sound_events"]

class DependenciesTypedDict(TypedDict):
    behavior_packs: NotRequired["BehaviorPacks"]
    blocks: NotRequired["MyBlocksClient"]
    credits: NotRequired["Credits"]
    duplicate_sounds: NotRequired["DuplicateSounds"]
    entities: NotRequired["Entities"]
    entities_client: NotRequired["EntitiesClient"]
    items: NotRequired["Items"]
    language: NotRequired["Language"]
    languages: NotRequired["Languages"]
    loading_tips: NotRequired["LoadingTips"]
    loot_tables: NotRequired["LootTables"]
    models: NotRequired["Models"]
    music_definitions: NotRequired["MyMusicDefinitions"]
    non_existent_sounds: NotRequired["NonExistentSounds"]
    recipes: NotRequired["Recipes"]
    resource_packs: NotRequired["ResourcePacks"]
    sound_definitions: NotRequired["MySoundDefinitionsJson"]
    sound_files: NotRequired["SoundFiles"]
    sounds_json: NotRequired["MySoundsJson"]
    splashes: NotRequired["Splashes"]
    trade_tables: NotRequired["TradeTables"]
    undefined_sound_events: NotRequired["UndefinedSoundEvents"]
    unused_sound_events: NotRequired["UnusedSoundEvents"]

# behavior packs

class BehaviorPackTypedDict(TypedDict):
    name: str
    path: str

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
    properties: dict[str,BlocksJsonClientBlockTypedDict]

class NormalizedBlocksJsonClientBlockTypedDict(TypedDict):
    blockshape: NotRequired[str]
    brightness_gamma: NotRequired[float]
    carried_textures: NotRequired[str|BlocksJsonBlockTexturesTypedDict]
    defined_in: NotRequired[list[str]]
    isotropic: NotRequired[bool|BlocksJsonBlockIsotropicTypedDict]
    sound: NotRequired[str]
    textures: NotRequired[str|BlocksJsonBlockTexturesTypedDict]

BlocksClient = dict[str,BlocksJsonClientBlockTypedDict]
MyBlocksClient = list[MyBlocksJsonClientBlockTypedDict]
NormalizedBlocksClient = dict[str,dict[str,NormalizedBlocksJsonClientBlockTypedDict]]

# credits

class CreditsTitleTypedDict(TypedDict):
    title: str
    names: list[str]

class CreditsDisciplineTypedDict(TypedDict):
    discipline: str
    titles: list[CreditsTitleTypedDict]

class CreditsSectionTypedDict(TypedDict):
    section: str
    disciplines: list[CreditsDisciplineTypedDict]
    titles: list[CreditsTitleTypedDict] # outdated

class NormalizedCreditsDisciplineTypedDict(TypedDict):
    discipline: str
    titles: dict[str, CreditsTitleTypedDict]

class NormalizedCreditsSectionTypedDict(TypedDict):
    section: str
    disciplines: dict[str, CreditsDisciplineTypedDict]
    titles: dict[str, CreditsTitleTypedDict] # outdated

Credits = list[CreditsSectionTypedDict]
NormalizedCredits = dict[str,CreditsSectionTypedDict]

# duplicate sounds

class DuplicateSoundsTypedDict(TypedDict):
    file_name: str
    file_internal_name: str

DuplicateSounds = dict[str,list[DuplicateSoundsTypedDict]]
NormalizedDuplicateSounds = dict[str,list[DuplicateSoundsTypedDict]]

# entities

Entities = dict[str,dict[str,Any]] # TODO: fill this out

# entities_client

EntitiesClient = dict[str,dict[str,Any]]  #TODO: fill this out

# items

Items = dict[str,dict[str,Any]] # TODO: fill this out

# language

class LanguageTypedDict(TypedDict):
    comment: NotRequired[str]
    value: Required[str]

Language = dict[str,dict[str,LanguageTypedDict]]

# languages

class NormalizedLanguagesPropertiesTypedDict():
    defined_in: list[str]

class LanguagesPropertiesTypedDict(TypedDict):
    name: NotRequired[str]

class NormalizedLanguagesTypedDict(TypedDict):
    code: str
    properties: dict[str,NormalizedLanguagesPropertiesTypedDict]

class LanguagesTypedDict(TypedDict):
    code: str
    defined_in: list[str]
    properties: dict[str,LanguagesPropertiesTypedDict]

Languages = list[LanguagesTypedDict]
NormalizedLanguages = dict[str,dict[str,LanguagesPropertiesTypedDict]]

# loading_tips

LoadingTips = dict[str,dict[str,list[str]]]

class LootTableConditions(TypedDict):
    condition: NotRequired[str]

class LootTableHasConditions(TypedDict):
    conditions: list[LootTableConditions]|dict[str,LootTableConditions]

class LootTableFunctions(TypedDict):
    function: NotRequired[str]

class LootTableHasFunctions(TypedDict):
    functions: list[LootTableFunctions]|dict[str,LootTableFunctions]

# loot_tables

LootTables = dict[str,dict[str,object]] # TODO: fill this out

# models

class ModelBoneTypedDict(TypedDict):
    bind_pose_rotation: list
    binding: str
    cubes: list
    inflate: float|int
    locators: dict
    material: str
    META_BoneType: None
    mirror: bool
    name: NotRequired[str]
    neverRender: bool
    parent: None
    pivot: list
    pos: list
    pre_rotation: list
    reset: bool
    rotation: list
    texture_meshes: list

class ModelGeometryTypedDict(TypedDict):
    bones: list[ModelBoneTypedDict]|dict[str,ModelBoneTypedDict]
    description: dict[str,Any]

Models = dict[str,dict[str,Any]] # TODO: fill this out

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
    name: str
    path: str

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
    exclude_from_pocket_platforms: NotRequired[bool]
    is3D: NotRequired[bool]
    load_on_low_memory: NotRequired[bool]
    name: NotRequired[str]
    pitch: NotRequired[float]
    stream: NotRequired[bool]
    type: NotRequired[str]
    volume: NotRequired[float]
    weight: NotRequired[int]

class SoundDefinitionsJsonSoundEventTypedDict(TypedDict):
    category: str
    max_distance: int|float
    min_distance: int|float
    sounds: list[str|SoundDefinitionsJsonSoundTypedDict]
    subtitle: str # unused

class NormalizedSoundDefinitionsJsonSoundEventTypedDict(TypedDict):
    category: str
    defined_in: NotRequired[list[str]]
    max_distance: int|float
    min_distance: int|float
    sounds: list[str|SoundDefinitionsJsonSoundTypedDict]|dict[str,NormalizedSoundDefinitionsJsonSoundTypedDict]
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
    _obj: NotRequired[str]
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
    sounds: NotRequired[str]
    volume: float|int|list[float|int]
    pitch: float|int|list[float|int]

class SoundsJsonSoundCollectionTypedDict(TypedDict):
    volume: float|list[float]
    pitch: float|list[float]
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
    volume: dict[str, float|list[float]]
    pitch: dict[str, float|list[float]]
    events: dict[str, dict[str, SoundsJsonSoundTypedDict]]|dict[str,dict[str,dict[str,str]]]

class MySoundsJsonTypedDict(TypedDict):
    individual_event_sounds: ResourcePackSoundsJsonFlatCollectionTypedDict
    block_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]
    interactive_block_sounds: dict[str, ResourcePackSoundsJsonFlatCollectionTypedDict]
    entity_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]
    interactive_entity_sounds: dict[str, ResourcePackSoundsJsonSoundCollectionTypedDict]

MySoundsJson = MySoundsJsonTypedDict

# splashes

class SplashesTypedDict(TypedDict):
    splashes: list[str]

SplashesFile = SplashesTypedDict
Splashes = dict[str,list[str]]

# TradeTables

TradeTables = dict[str,dict[str,dict[str,Any]]] # TODO: fill this out

# undefined_sound_events

UndefinedSoundEvents = dict[str,list[list[str]]] # TODO: fill this out

# unused_sound_events

UnusedSoundEvents = list[str]
