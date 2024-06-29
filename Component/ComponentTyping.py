from typing import (TYPE_CHECKING, Any, Callable, Literal, TypeAlias,
                    TypedDict, Union)

from typing_extensions import NotRequired, Required

if TYPE_CHECKING:
    import Component.Component as Component
    import Utilities.TypeVerifier.TypeVerifierImporter as TypeVerifierImporter

class AccessorTypedDict(TypedDict):
    accessor_type: Required[str]
    arguments: Required[dict[str,Any]]
    type: NotRequired[Literal["Accessor"]]

class AccessorTypeTypedDict(TypedDict):
    accessor_class: Required[str]
    manager_class: Required[str]
    parameters: Required["TypeVerifierImporter.TypedVerifierTypedDicts"]
    type: NotRequired[Literal["AccessorType"]]

ImportedComponentTypedDict = TypedDict("ImportedComponentTypedDict", {"as": NotRequired[str], "component": Required[str]})

ImportTypedDict = TypedDict("ImportTypedDict", {"components": Required[list[ImportedComponentTypedDict]], "from": Required[str]})

class BaseTypedDict(TypedDict):
    imports: NotRequired[list[ImportTypedDict]]
    name: Required[str]
    normalizer: NotRequired[str|list[str]]
    subcomponent: Required[str]
    type: NotRequired[Literal["Base"]]

class CacheTypedDict(TypedDict):
    cache_check_all_types: NotRequired[bool]
    cache_compare: NotRequired[bool]
    cache_compare_text: NotRequired[bool]
    cache_get_tag_paths: NotRequired[bool]
    cache_normalize: NotRequired[bool]
    cache_print_text: NotRequired[bool]
    subcomponent: Required[str]
    type: NotRequired[Literal["Cache"]]
    types: Required[str|list[str]]

class DataMinerCollectionTypedDict(TypedDict):
    dataminers: Required[list["DataMinerSettingsTypedDict"]]
    disabled: NotRequired[bool]
    file_name: Required[str]
    structure: Required[str]
    type: NotRequired[Literal["DataMinerCollection"]]

class DataMinerSettingsTypedDict(TypedDict):
    dependencies: NotRequired[list[str]]
    files: NotRequired[list[str]]
    name: Required[str|None]
    new: Required[str|None]
    old: Required[str|None]
    parameters: NotRequired[dict[str,Any]]
    type: NotRequired[Literal["DataMinerSettings"]]

class DictTypedDict(TypedDict):
    detect_key_moves: NotRequired[bool]
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    min_key_similarity_threshold: NotRequired[float]
    min_value_similarity_threshold: NotRequired[float]
    normalizer: NotRequired[str|list[str]]
    print_all: NotRequired[bool]
    sort: NotRequired[Literal["none", "by_key", "by_value"]]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["Dict"]]
    types: Required[str|list[str]]

class GroupTypedDict(TypedDict):
    subcomponents: Required[dict[str,str|None]]
    type: NotRequired[Literal["Group"]]

class KeymapKeyTypedDict(TypedDict):
    matters_for_similarity: NotRequired[bool]
    subcomponent: NotRequired[Union[str,None,"StructureTypedDicts"]]
    tags: NotRequired[str|list[str]]
    type: Required[str|list[str]]

class KeymapTypedDict(TypedDict):
    detect_key_moves: NotRequired[bool]
    field: NotRequired[str]
    imports: NotRequired[str|list[str]]
    keys: Required[dict[str,KeymapKeyTypedDict]]
    measure_length: NotRequired[bool]
    min_key_similarity_threshold: NotRequired[float]
    min_value_similarity_threshold: NotRequired[float]
    normalizer: NotRequired[str|list[str]]
    sort: NotRequired[Literal["none", "by_key", "by_value", "by_component_order"]]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["Keymap"]]

class LatestSlotTypedDict(TypedDict):
    ...

class ListTypedDict(TypedDict):
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    ordered: NotRequired[bool]
    print_all: NotRequired[bool]
    print_flat: NotRequired[bool]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["List"]]
    types: Required[str|list[str]]

class NbtBaseTypedDict(TypedDict):
    endianness: Required[Literal["big", "little"]]
    normalizer: NotRequired[str|list[str]]
    subcomponent: Required[str]
    type: NotRequired[Literal["NbtBase"]]
    types: Required[str|list[str]]

class NormalizerTypedDict(TypedDict):
    function_name: Required[str]
    type: NotRequired[Literal["Normalizer"]]

class PrimitiveComponentTypedDict(TypedDict):
    normalizer: NotRequired[str|list[str]]
    tags: NotRequired[str|list[str]]
    type: NotRequired[Literal["Primitive"]]
    types: Required[str|list[str]]

class RangeVersionTagAutoAssignerTypedDict(TypedDict):
    newest: Required[str|None]
    oldest: Required[str|None]
    type: NotRequired[Literal["RangeVersionTagAutoAssign"]]

class SetTypedDict(TypedDict):
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    min_similarity_threshold: NotRequired[float]
    normalizer: NotRequired[str|list[str]]
    ordered: NotRequired[bool]
    print_all: NotRequired[bool]
    print_flat: NotRequired[bool]
    sort: NotRequired[bool]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["List"]]
    types: Required[str|list[str]]

class StringComponentTypedDict(TypedDict):
    normalizer: NotRequired[str|list[str]]
    tags: NotRequired[str|list[str]]
    type: NotRequired[Literal["Primitive"]]
    types: NotRequired[str|list[str]]

class TagTypedDict(TypedDict):
    type: NotRequired[Literal["Tag"]]

class TypeAliasTypedDict(TypedDict):
    type: NotRequired[Literal["TypeAlias"]]
    types: Required[str|list[str]]

class VersionFileTypedDict(TypedDict):
    accessors: Required[list[AccessorTypedDict]]
    type: NotRequired[Literal["VersionFileType"]]
    version_file_type: Required[str]

class VersionFileTypeTypedDict(TypedDict):
    allowed_accessor_types: Required[list[str]]
    auto_assign: NotRequired[AccessorTypedDict]
    available_when_unreleased: Required[bool]
    install_location: Required[str]
    must_exist: Required[bool]

class VersionTagOrderTypedDict(TypedDict):
    allowed_children: Required[dict[str,list[str]]]
    order: Required[list[list[str]]]
    tags_after_top_level_tag: Required[list[str]]
    tags_before_top_level_tag: Required[list[str]]
    top_level_tag: Required[str]
    type: NotRequired[Literal["VersionTagOrder"]]

class VersionTagTypedDict(TypedDict):
    auto_assign: NotRequired["AutoAssignerTypedDicts"]
    development_name: NotRequired[str]
    is_development_tag: NotRequired[bool]
    is_fork_tag: NotRequired[bool]
    is_major_tag: NotRequired[bool]
    is_order_tag: NotRequired[bool]
    latest_slot: NotRequired[str]
    type: NotRequired[Literal["VersionTag"]]

class VersionTypedDict(TypedDict):
    files: Required[dict[str,dict[str,Any]]]
    id: Required[str]
    parent: Required[str|None]
    tags: Required[list[str]]
    time: Required[str|None]
    type: NotRequired[Literal["Version"]]

class VolumeTypedDict(TypedDict):
    field: NotRequired[str]
    normalizer: NotRequired[str|list[str]]
    position_key: Required[str]
    print_additional_data: NotRequired[bool]
    state_key: Required[str]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["Volume"]]
    types: Required[str|list[str]]

AutoAssignerTypedDicts:TypeAlias = RangeVersionTagAutoAssignerTypedDict
ComponentTypedDicts:TypeAlias = Union[
    AccessorTypedDict,
    AccessorTypeTypedDict,
    BaseTypedDict,
    CacheTypedDict,
    DataMinerCollectionTypedDict,
    DataMinerSettingsTypedDict,
    DictTypedDict,
    GroupTypedDict,
    KeymapTypedDict,
    LatestSlotTypedDict,
    ListTypedDict,
    NbtBaseTypedDict,
    NormalizerTypedDict,
    RangeVersionTagAutoAssignerTypedDict,
    TagTypedDict,
    TypeAliasTypedDict,
    VersionFileTypedDict,
    VersionFileTypeTypedDict,
    VersionTagOrderTypedDict,
    VersionTagTypedDict,
    VersionTypedDict,
    VolumeTypedDict,
]
StructureTypedDicts:TypeAlias = CacheTypedDict|DictTypedDict|GroupTypedDict|KeymapTypedDict|NbtBaseTypedDict|ListTypedDict|VolumeTypedDict

ComponentGroupFileType:TypeAlias = dict[str,ComponentTypedDicts]
CreateComponentFunction:TypeAlias = Callable[[ComponentTypedDicts,"Component.Component",str|None],"Component.Component"]
