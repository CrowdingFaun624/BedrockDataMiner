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
    default_delegate: NotRequired[str]
    default_delegate_arguments: NotRequired[dict[str,Any]]
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    imports: NotRequired[list[ImportTypedDict]]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    subcomponent: Required[str]
    type: NotRequired[Literal["Base"]]

class CacheTypedDict(TypedDict):
    cache_check_all_types: NotRequired[bool]
    cache_compare: NotRequired[bool]
    cache_compare_text: NotRequired[bool]
    cache_get_similarity: NotRequired[bool]
    cache_get_tag_paths: NotRequired[bool]
    cache_normalize: NotRequired[bool]
    cache_print_text: NotRequired[bool]
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
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
    arguments: NotRequired[dict[str,Any]]
    dependencies: NotRequired[list[str]]
    files: NotRequired[list[str]]
    name: Required[str|None]
    new: Required[str|None]
    old: Required[str|None]
    type: NotRequired[Literal["DataMinerSettings"]]

class DictTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    detect_key_moves: NotRequired[bool]
    key_component: NotRequired[str]
    key_weight: NotRequired[float]
    min_key_similarity_threshold: NotRequired[float]
    min_value_similarity_threshold: NotRequired[float]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    required_keys: NotRequired[list[str]]
    sort: NotRequired[Literal["none", "by_key", "by_value"]]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["Dict"]]
    types: Required[str|list[str]]
    value_weight: NotRequired[float]

class GroupTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[list[str]]
    subcomponents: Required[dict[str,str|None]]
    type: NotRequired[Literal["Group"]]

class KeymapKeyTypedDict(TypedDict):
    delegate_arguments: NotRequired[dict[str,Any]]
    required: NotRequired[bool]
    subcomponent: NotRequired[Union[str,None,"StructureTypedDicts"]]
    tags: NotRequired[str|list[str]]
    type: Required[str|list[str]]
    weight: NotRequired[int]

class KeymapTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    detect_key_moves: NotRequired[bool]
    imports: NotRequired[str|list[str]]
    key_component: NotRequired[str]
    key_weight: NotRequired[float]
    keys: Required[dict[str,KeymapKeyTypedDict]]
    min_key_similarity_threshold: NotRequired[float]
    min_value_similarity_threshold: NotRequired[float]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    sort: NotRequired[Literal["none", "by_key", "by_value", "by_component_order"]]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["Keymap"]]
    value_weight: NotRequired[float]

class LatestSlotTypedDict(TypedDict):
    type: NotRequired[Literal["LatestSlot"]]

class ListTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["List"]]
    types: Required[str|list[str]]

class NbtBaseTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    endianness: Required[Literal["big", "little"]]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    subcomponent: Required[str]
    type: NotRequired[Literal["NbtBase"]]
    types: Required[str|list[str]]

class NormalizerTypedDict(TypedDict):
    function_name: Required[str]
    type: NotRequired[Literal["Normalizer"]]

class PrimitiveComponentTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    tags: NotRequired[str|list[str]]
    type: NotRequired[Literal["Primitive"]]
    types: Required[str|list[str]]

class RangeVersionTagAutoAssignerTypedDict(TypedDict):
    newest: Required[str|None]
    oldest: Required[str|None]
    type: NotRequired[Literal["RangeVersionTagAutoAssign"]]

class SetTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    min_similarity_threshold: NotRequired[float]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    sort: NotRequired[bool]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["List"]]
    types: Required[str|list[str]]

class StringComponentTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
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
]
StructureTypedDicts:TypeAlias = CacheTypedDict|DictTypedDict|GroupTypedDict|KeymapTypedDict|NbtBaseTypedDict|ListTypedDict

ComponentGroupFileType:TypeAlias = dict[str,ComponentTypedDicts]
CreateComponentFunction:TypeAlias = Callable[[ComponentTypedDicts,"Component.Component",str|None],"Component.Component"]
