from typing import (TYPE_CHECKING, Any, Callable, Literal, NotRequired,
                    Required, TypedDict)

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
    pre_normalized_types: NotRequired[str|list[str]]
    subcomponent: Required[str]
    type: NotRequired[Literal["Base"]]
    types: Required[str|list[str]]

class CacheTypedDict(TypedDict):
    cache_check_all_types: NotRequired[bool]
    cache_compare: NotRequired[bool]
    cache_compare_text: NotRequired[bool]
    cache_get_referenced_files: NotRequired[bool]
    cache_get_similarity: NotRequired[bool]
    cache_get_tag_paths: NotRequired[bool]
    cache_normalize: NotRequired[bool]
    cache_print_text: NotRequired[bool]
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    remove_threshold: NotRequired[int]
    subcomponent: Required[str]
    type: NotRequired[Literal["Cache"]]
    types: Required[str|list[str]]

class CoverageDataminerCollectionTypedDict(TypedDict):
    comparing_disabled: NotRequired[bool]
    disabled: NotRequired[bool]
    file_list_dataminer: Required[str]
    file_name: Required[str]
    remove_files: NotRequired[list[str]]
    remove_regex: NotRequired[list[str]]
    remove_prefixes: NotRequired[list[str]]
    remove_suffixes: NotRequired[list[str]]
    structure: str
    type: Literal["CoverageDataminerCollection"]

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
    serializer: NotRequired[str|dict[str,str]]
    type: NotRequired[Literal["DataminerSettings"]]

class DictTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    detect_key_moves: NotRequired[bool]
    key_component: NotRequired[str]
    key_weight: NotRequired[float]
    max_key_similarity_descendent_depth: NotRequired[int|None]
    max_similarity_ancestor_depth: NotRequired[int|None]
    max_similarity_descendent_depth: NotRequired[int|None]
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

class FileTypedDict(TypedDict):
    content_types: Required[str|list[str]]
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    file_types: NotRequired[str|list[str]]
    garbage_collect: NotRequired[bool]
    max_similarity_ancestor_depth: NotRequired[int|None]
    max_similarity_descendent_depth: NotRequired[int|None]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    subcomponent: Required[str|None]
    type: NotRequired[Literal["Passthrough"]]

class GroupTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    max_similarity_ancestor_depth: NotRequired[int|None]
    max_similarity_descendent_depth: NotRequired[int|None]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[list[str]]
    subcomponents: Required[dict[str,str|None]]
    type: NotRequired[Literal["Group"]]

class KeymapKeyTypedDict(TypedDict):
    delegate_arguments: NotRequired[dict[str,Any]]
    max_similarity_descendent_depth: NotRequired[int|None]
    required: NotRequired[bool]
    subcomponent: NotRequired["str|None|StructureTypedDicts"]
    tags: NotRequired[str|list[str]]
    type: Required[str|list[str]]
    weight: NotRequired[int]

class KeymapTypedDict(TypedDict):
    default_max_similarity_descendent_depth: NotRequired[int|None]
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    detect_key_moves: NotRequired[bool]
    imports: NotRequired[str|list[str]]
    key_component: NotRequired[str]
    key_weight: NotRequired[float]
    keys: Required[dict[str,KeymapKeyTypedDict]]
    max_key_similarity_descendent_depth: NotRequired[int|None]
    max_similarity_ancestor_depth: NotRequired[int|None]
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
    max_similarity_ancestor_depth: NotRequired[int|None]
    max_similarity_descendent_depth: NotRequired[int|None]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["List"]]
    types: Required[str|list[str]]

class LogTypedDict(TypedDict):
    file_name: Required[str]
    log_type: Required[str]
    reset_on_reload: Required[bool]
    type: NotRequired[Literal["Log"]]

class NormalizerTypedDict(TypedDict):
    arguments: NotRequired[dict[str,Any]]
    function_name: Required[str]
    type: NotRequired[Literal["Normalizer"]]
    version_range: NotRequired[list[str|None]]

class PrimitiveTypedDict(TypedDict):
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

class SequenceTypedDict(TypedDict):
    addition_cost: NotRequired[int|float]
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    deletion_cost: NotRequired[int|float]
    max_similarity_ancestor_depth: NotRequired[int|None]
    max_similarity_descendent_depth: NotRequired[int|None]
    normalizer: NotRequired[str|list[str]]
    post_normalizer: NotRequired[str|list[str]]
    pre_normalized_types: NotRequired[str|list[str]]
    subcomponent: Required[str|None]
    substitution_cost: NotRequired[int|float]
    tags: NotRequired[str|list[str]]
    this_type: NotRequired[str|list[str]]
    type: NotRequired[Literal["List"]]
    types: Required[str|list[str]]

class SerializerTypedDict(TypedDict):
    arguments: NotRequired[dict[str,Any]]
    serializer_class: Required[str]
    type: NotRequired[Literal["Serializer"]]

class SetTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    max_similarity_ancestor_depth: NotRequired[int|None]
    max_similarity_descendent_depth: NotRequired[int|None]
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

class StringTypedDict(TypedDict):
    delegate: NotRequired[str]
    delegate_arguments: NotRequired[dict[str,Any]]
    max_similarity_ancestor_depth: NotRequired[int|None]
    normalizer: NotRequired[str|list[str]]
    similarity_function: NotRequired[str|None]
    tags: NotRequired[str|list[str]]
    type: NotRequired[Literal["Primitive"]]
    types: NotRequired[str|list[str]]

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

type AutoAssignerTypedDicts = RangeVersionTagAutoAssignerTypedDict
type ComponentTypedDicts = \
    AccessorTypedDict|\
    AccessorTypeTypedDict|\
    BaseTypedDict|\
    CacheTypedDict|\
    CoverageDataminerCollectionTypedDict|\
    DataminerCollectionTypedDict|\
    DataminerSettingsTypedDict|\
    DictTypedDict|\
    FileTypedDict|\
    GroupTypedDict|\
    KeymapTypedDict|\
    LatestSlotTypedDict|\
    ListTypedDict|\
    NormalizerTypedDict|\
    PrimitiveTypedDict|\
    RangeVersionTagAutoAssignerTypedDict|\
    SequenceTypedDict|\
    SerializerTypedDict|\
    SetTypedDict|\
    StringTypedDict|\
    StructureTagTypedDict|\
    TablifierTypedDict|\
    TypeAliasTypedDict|\
    VersionFileTypedDict|\
    VersionFileTypeTypedDict|\
    VersionTagOrderTypedDict|\
    VersionTagTypedDict|\
    VersionTypedDict

type StructureTypedDicts = CacheTypedDict|DictTypedDict|GroupTypedDict|KeymapTypedDict|ListTypedDict|FileTypedDict|PrimitiveTypedDict|SequenceTypedDict|SetTypedDict|StringTypedDict

type ComponentGroupFileType = dict[str,ComponentTypedDicts]
type CreateComponentFunction = Callable[[ComponentTypedDicts,"Component.Component",str|None],"Component.Component"]
