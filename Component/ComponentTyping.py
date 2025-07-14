from types import EllipsisType
from typing import Any, Callable, Literal, NotRequired, Required, TypedDict

from Component.Component import Component


class AccessorTypedDict(TypedDict):
    accessor_type: Required[str]
    arguments: Required[dict[str,Any]]
    type: NotRequired[Literal["Accessor"]]

class AccessorTypeTypedDict(TypedDict):
    accessor_class: Required[str]
    arguments: NotRequired[dict[str,Any]]
    linked_accessors: NotRequired[dict[str,"ComponentTypedDicts|str"]]
    type: NotRequired[Literal["AccessorType"]]

class CoverageDataminerCollectionTypedDict(TypedDict):
    comparing_disabled: NotRequired[bool]
    disabled: NotRequired[bool]
    file: Required[str]
    file_list_dataminer: Required[str]
    file_name: Required[str]
    remove_files: NotRequired[list[str]]
    remove_regex: NotRequired[list[str]]
    remove_prefixes: NotRequired[list[str]]
    remove_suffixes: NotRequired[list[str]]
    structure: Required[str]
    structure_info: NotRequired[dict[str,Any]]
    type: NotRequired[Literal["CoverageDataminerCollection"]]

class DataminerCollectionTypedDict(TypedDict):
    comparing_disabled: NotRequired[bool]
    dataminers: Required[list["DataminerSettingsTypedDict"]]
    disabled: NotRequired[bool]
    file_name: Required[str]
    structure: Required[str]
    type: NotRequired[Literal["DataminerCollection"]]

class DataminerSettingsTypedDict(TypedDict):
    arguments: NotRequired[dict[str,Any]]
    dependencies: NotRequired[list[str]]
    files: NotRequired[list[str]]
    name: Required[str|None]
    new: Required[str|None]
    old: Required[str|None]
    structure_info: NotRequired[dict[str,Any]]
    type: NotRequired[Literal["DataminerSettings"]]

class KeyFilterTypedDict(TypedDict):
    key: Required[str]
    type: NotRequired[str]

class LatestSlotTypedDict(TypedDict):
    type: NotRequired[Literal["LatestSlot"]]

class LogTypedDict(TypedDict):
    file_name: Required[str]
    log_type: Required[str]
    reset_on_reload: Required[bool]
    type: NotRequired[Literal["Log"]]

class MetaFilterTypedDict(TypedDict):
    subfilters: Required[list["ComponentTypedDicts"]]
    type: NotRequired[str]

class NormalizerTypedDict(TypedDict):
    arguments: NotRequired[dict[str,Any]]
    function_name: Required[str]
    type: NotRequired[Literal["Normalizer"]]
    filter: NotRequired["str|ComponentTypedDicts|None"]

class RangeVersionTagAutoAssignerTypedDict(TypedDict):
    newest: Required[str|None]
    oldest: Required[str|None]
    type: NotRequired[Literal["RangeVersionTagAutoAssign"]]

class SerializerTypedDict(TypedDict):
    arguments: NotRequired[dict[str,Any]]
    serializer_class: Required[str]
    type: NotRequired[Literal["Serializer"]]

class StructureTagTypedDict(TypedDict):
    is_file: NotRequired[bool]
    type: NotRequired[Literal["StructureTag"]]

class TablifierTypedDict(TypedDict):
    dataminer_collection: Required[str]
    file_name: Required[str]
    structure: Required[str]
    type: NotRequired[Literal["Tablifier"]]
    version_provider: Required[str]

class TypeAliasTypedDict(TypedDict):
    type: NotRequired[Literal["TypeAlias"]]
    types: Required[list[str]]

class ValueFilterTypedDict(TypedDict):
    default: NotRequired[bool]
    key: Required[str]
    type: NotRequired[str]
    value: Required[object]

class VersionFileTypedDict(TypedDict):
    accessors: Required[list[AccessorTypedDict]]
    type: NotRequired[Literal["VersionFileType"]]
    version_file_type: Required[str]

class VersionFileTypeTypedDict(TypedDict):
    allowed_accessor_types: Required[list[str]]
    auto_assign: NotRequired[AccessorTypedDict]
    available_when_unreleased: Required[bool]
    must_exist: Required[bool]

class VersionTagOrderTypedDict(TypedDict):
    allowed_children: Required[dict[str,list[str]]]
    order: Required[list[list[str]]]
    tags_after_top_level_tag: Required[list[str]]
    tags_before_top_level_tag: Required[list[str]]
    top_level_tag: Required[str|None]
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

# STRUCTURE COMPONENTS

class StructureTypedDict(TypedDict):
    pass

class IterableStructureTypedDict(StructureTypedDict):
    delegate: NotRequired[str|None]
    delegate_arguments: NotRequired[dict[str,Any]]
    key_function: NotRequired[str]
    key_types: NotRequired[str|list[str]]
    normalizers: NotRequired["str|ComponentTypedDicts|list[str|ComponentTypedDicts]"]
    post_normalizers: NotRequired["str|ComponentTypedDicts|list[str|ComponentTypedDicts]"]
    pre_normalized_types: NotRequired[str|list[str]]
    required_keys: NotRequired[list[str]]
    tags: NotRequired[str|list[str]]
    this_types: Required[str|list[str]]

class PassthroughStructureTypedDict(StructureTypedDict):
    normalizers: NotRequired["str|ComponentTypedDicts|list[str|ComponentTypedDicts]"]
    post_normalizers: NotRequired["str|ComponentTypedDicts|list[str|ComponentTypedDicts]"]
    pre_normalized_types: NotRequired[str|list[str]]
    tags: NotRequired[str|list[str]]

class BranchlessStructureTypedDict(PassthroughStructureTypedDict):
    structure: Required["str|ComponentTypedDicts|None"]
    this_types: Required[str|list[str]]

class PrimitiveStructureTypedDict(StructureTypedDict):
    delegate: NotRequired[str|None]
    delegate_arguments: NotRequired[dict[str,Any]]
    normalizers: NotRequired["str|ComponentTypedDicts|list[str|ComponentTypedDicts]"]
    pre_normalized_types: NotRequired[str|list[str]]
    tags: NotRequired[str|list[str]]
    this_types: NotRequired[str|list[str]]

class MappingStructureTypedDict(IterableStructureTypedDict):
    min_key_similarity_threshold: NotRequired[float]
    min_value_similarity_threshold: NotRequired[float]

class CacheStructureTypedDict(BranchlessStructureTypedDict):
    removal_threshold: NotRequired[int]
    delegate: NotRequired[str|None]
    delegate_arguments: NotRequired[dict[str,Any]]

class ConditionStructureItemTypedDict(TypedDict):
    filter: Required["str|ComponentTypedDicts|None"]
    structure: NotRequired["str|ComponentTypedDicts|None"]
    types: Required[str|list[str]]

class ConditionStructureTypedDict(PassthroughStructureTypedDict):
    substructures: Required[list[ConditionStructureItemTypedDict]]

class DictStructureTypedDict(MappingStructureTypedDict):
    allow_key_moves: NotRequired[bool]
    allow_same_key_optimization: NotRequired[bool|None]
    key_structure: NotRequired["str|ComponentTypedDicts|None"]
    key_weight: NotRequired[int]
    value_structure: Required["str|ComponentTypedDicts|None"]
    value_types: Required[str|list[str]]
    value_weight: NotRequired[int]

class FileStructureTypedDict(PassthroughStructureTypedDict):
    content_types: Required[str|list[str]]
    file_types: NotRequired[str|list[str]]
    serializer: Required["str|ComponentTypedDicts"]
    structure: Required["str|ComponentTypedDicts|None"]

class KeyTypedDict(TypedDict):
    delegate_arguments: NotRequired[dict[str,Any]]
    required: NotRequired[bool]
    similarity_weight: NotRequired[int]
    structure: NotRequired["str|ComponentTypedDicts|None"]
    tags: NotRequired[str|list[str]]
    types: Required[str|list[str]]
    value_weight: NotRequired[int|None]

class KeymapStructureTypedDict(MappingStructureTypedDict):
    allow_key_moves: NotRequired[bool]
    imports: NotRequired[str|list[str]]
    key_structure: NotRequired["str|ComponentTypedDicts|None"]
    key_weight: NotRequired[int]
    keys: NotRequired[dict[str,KeyTypedDict]]
    value_weight: NotRequired[int]

class NumberStructureTypedDict(PrimitiveStructureTypedDict):
    normal_value: Required[float|int]
    similarity_function: NotRequired[str]

class SequenceStructureTypedDict(IterableStructureTypedDict):
    addition_cost: NotRequired[float]
    deletion_cost: NotRequired[float]
    key_structure: NotRequired["str|ComponentTypedDicts|None"]
    key_weight: NotRequired[int|None]
    max_square_length: NotRequired[int]
    substitution_cost: NotRequired[float]
    value_structure: Required["str|ComponentTypedDicts|None"]
    value_types: Required[str|list[str]]
    value_weight: NotRequired[int]

class StringStructureTypedDict(PrimitiveStructureTypedDict):
    max_square_length: NotRequired[int]
    similarity_function: NotRequired[str]
    similarity_weight_function: NotRequired[str]

class StructureBaseTypedDict(BranchlessStructureTypedDict):
    default_delegate: NotRequired[str|None]
    default_delegate_arguments: NotRequired[dict[str,Any]]
    delegate: NotRequired[str|None]
    delegate_arguments: NotRequired[dict[str,Any]]


class SwitchStructureTypedDict(PassthroughStructureTypedDict):
    switch_function: Required[str]
    substructures: Required[dict[str, KeyTypedDict]]

class UnionStructureTypedDict(PassthroughStructureTypedDict):
    substructures: Required[dict[str, "str|ComponentTypedDicts|None"]]

class InheritedComponentTypedDict(TypedDict):
    inherit: Required[str]

type AutoAssignerTypedDicts = RangeVersionTagAutoAssignerTypedDict
type ComponentTypedDicts = \
    AccessorTypedDict|\
    AccessorTypeTypedDict|\
    BranchlessStructureTypedDict|\
    CacheStructureTypedDict|\
    ConditionStructureTypedDict|\
    CoverageDataminerCollectionTypedDict|\
    DataminerCollectionTypedDict|\
    DataminerSettingsTypedDict|\
    DictStructureTypedDict|\
    FileStructureTypedDict|\
    IterableStructureTypedDict|\
    KeymapStructureTypedDict|\
    LatestSlotTypedDict|\
    MappingStructureTypedDict|\
    MetaFilterTypedDict|\
    NormalizerTypedDict|\
    NumberStructureTypedDict|\
    PassthroughStructureTypedDict|\
    PrimitiveStructureTypedDict|\
    RangeVersionTagAutoAssignerTypedDict|\
    SequenceStructureTypedDict|\
    SerializerTypedDict|\
    StringStructureTypedDict|\
    StructureBaseTypedDict|\
    StructureTagTypedDict|\
    StructureTypedDict|\
    SwitchStructureTypedDict|\
    TablifierTypedDict|\
    TypeAliasTypedDict|\
    UnionStructureTypedDict|\
    ValueFilterTypedDict|\
    VersionFileTypedDict|\
    VersionFileTypeTypedDict|\
    VersionTagOrderTypedDict|\
    VersionTagTypedDict|\
    VersionTypedDict|\
    InheritedComponentTypedDict

type GroupFileType = dict[str,ComponentTypedDicts]
type CreateComponentFunction = Callable[[ComponentTypedDicts,"Component",str|None,tuple[str,...]],"Component|EllipsisType"]
