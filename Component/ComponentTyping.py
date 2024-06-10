from typing import (TYPE_CHECKING, Any, Callable, Literal, TypeAlias,
                    TypedDict, Union)

from typing_extensions import NotRequired, Required

if TYPE_CHECKING:
    import Component.Component as Component

ImportedComponentTypedDict = TypedDict("ImportedComponentTypedDict", {"as": NotRequired[str], "component": Required[str]})

ImportTypedDict = TypedDict("ImportTypedDict", {"from": Required[str], "components": Required[list[ImportedComponentTypedDict]]})

class BaseComponentTypedDict(TypedDict):
    subcomponent: Required[str]
    imports: NotRequired[list[ImportTypedDict]]
    name: Required[str]
    normalizer: NotRequired[str|list[str]]
    type: NotRequired[Literal["Base"]]

class CacheComponentTypedDict(TypedDict):
    type: NotRequired[Literal["Cache"]]
    types: Required[str|list[str]]
    subcomponent: Required[str]
    cache_check_all_types: NotRequired[bool]
    cache_normalize: NotRequired[bool]
    cache_get_tag_paths: NotRequired[bool]
    cache_compare_text: NotRequired[bool]
    cache_print_text: NotRequired[bool]
    cache_compare: NotRequired[bool]

class DataMinerCollectionComponentTypedDict(TypedDict):
    type: NotRequired[Literal["DataMinerCollection"]]
    file_name: Required[str]
    structure: Required[str]
    disabled: NotRequired[bool]
    dataminers: Required[list["DataMinerSettingsComponentTypedDict"]]

class DataMinerSettingsComponentTypedDict(TypedDict):
    type: NotRequired[Literal["DataMinerSettings"]]
    new: Required[str|None]
    old: Required[str|None]
    name: Required[str|None]
    files: NotRequired[list[str]]
    dependencies: NotRequired[list[str]]
    parameters: NotRequired[dict[str,Any]]

class DictComponentTypedDict(TypedDict):
    subcomponent: Required[str|None]
    comparison_move_function: NotRequired[str]
    detect_key_moves: NotRequired[bool]
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    type: NotRequired[Literal["Dict"]]
    print_all: NotRequired[bool]
    types: Required[str|list[str]]
    tags: NotRequired[str|list[str]]

class GroupComponentTypedDict(TypedDict):
    type: NotRequired[Literal["Group"]]
    subcomponents: Required[dict[str,str|None]]

class KeymapKeyTypedDict(TypedDict):
    type: Required[str|list[str]]
    subcomponent: NotRequired[Union[str,None,"StructroidComponentTypedDicts"]]
    tags: NotRequired[str|list[str]]

class KeymapComponentTypedDict(TypedDict):
    field: NotRequired[str]
    imports: NotRequired[str|list[str]]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    tags: NotRequired[str|list[str]]
    type: NotRequired[Literal["Keymap"]]
    keys: Required[dict[str,KeymapKeyTypedDict]]

class ListComponentTypedDict(TypedDict):
    subcomponent: Required[str|None]
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    ordered: NotRequired[bool]
    print_all: NotRequired[bool]
    print_flat: NotRequired[bool]
    type: NotRequired[Literal["List"]]
    types: Required[str|list[str]]
    tags: NotRequired[str|list[str]]

class NbtBaseTypedDict(TypedDict):
    subcomponent: Required[str]
    endianness: Required[Literal["big", "little"]]
    normalizer: NotRequired[str|list[str]]
    type: NotRequired[Literal["NbtBase"]]
    types: Required[str|list[str]]

class NormalizerTypedDict(TypedDict):
    dependencies: Required[list[str]]
    function_name: Required[str]
    type: NotRequired[Literal["Normalizer"]]

class TagTypedDict(TypedDict):
    type: NotRequired[Literal["Tag"]]

class TypeAliasTypedDict(TypedDict):
    type: NotRequired[Literal["TypeAlias"]]
    types: Required[str|list[str]]

class VolumeTypedDict(TypedDict):
    field: NotRequired[str]
    normalizer: NotRequired[str|list[str]]
    position_key: Required[str]
    print_additional_data: NotRequired[bool]
    state_key: Required[str]
    subcomponent: Required[str|None]
    tags: NotRequired[str|list[str]]
    this_type: Required[str]
    type: NotRequired[Literal["Volume"]]
    types: Required[str|list[str]]

ComponentTypedDicts:TypeAlias = BaseComponentTypedDict|CacheComponentTypedDict|DataMinerCollectionComponentTypedDict|DataMinerSettingsComponentTypedDict|DictComponentTypedDict|GroupComponentTypedDict|KeymapComponentTypedDict|ListComponentTypedDict|NbtBaseTypedDict|NormalizerTypedDict|TypeAliasTypedDict|VolumeTypedDict
StructureComponentTypedDicts:TypeAlias = DictComponentTypedDict|KeymapComponentTypedDict|ListComponentTypedDict
StructroidComponentTypedDicts:TypeAlias = CacheComponentTypedDict|DictComponentTypedDict|GroupComponentTypedDict|KeymapComponentTypedDict|ListComponentTypedDict|VolumeTypedDict
ComponentGroupFileType:TypeAlias = dict[str,ComponentTypedDicts]

CreateComponentFunction:TypeAlias = Callable[[ComponentTypedDicts,"Component.Component",str|None],"Component.Component"]
