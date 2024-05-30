from typing import Literal, TypedDict

from typing_extensions import NotRequired, Required

import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes

ImportedComponentTypedDict = TypedDict("ImportedComponentTypedDict", {"as": NotRequired[str], "component": Required[str]})

ImportTypedDict = TypedDict("ImportTypedDict", {"from": Required[str], "components": Required[list[ImportedComponentTypedDict]]})

class BaseComponentTypedDict(TypedDict):
    subcomponent: Required[str]
    imports: NotRequired[list[ImportTypedDict]]
    name: Required[str]
    normalizer: NotRequired[str]
    post_normalizer: NotRequired[str]
    type: Required[Literal["Base"]]

class CacheComponentTypedDict(TypedDict):
    type: Required[Literal["Cache"]]
    types: Required[list[str]]
    subcomponent: Required[str]
    cache_check_all_types: NotRequired[bool]
    cache_normalize: NotRequired[bool]
    cache_get_tag_paths: NotRequired[bool]
    cache_compare_text: NotRequired[bool]
    cache_print_text: NotRequired[bool]
    cache_compare: NotRequired[bool]

class DictComponentTypedDict(TypedDict):
    subcomponent: Required[str|None]
    comparison_move_function: NotRequired[str]
    detect_key_moves: NotRequired[bool]
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    type: Required[Literal["Dict"]]
    print_all: NotRequired[bool]
    types: Required[list[str]]

class GroupComponentTypedDict(TypedDict):
    type: Required[Literal["Group"]]
    subcomponents: Required[dict[str,str|None]]

class KeymapKeyTypedDict(TypedDict):
    type: Required[str|list[str]]
    subcomponent: NotRequired[str|None]
    tags: NotRequired[str|list[str]]

class KeymapComponentTypedDict(TypedDict):
    field: NotRequired[str]
    imports: NotRequired[str|list[str]]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    tags: NotRequired[list[str]]
    type: Required[Literal["Keymap"]]
    keys: Required[dict[str,KeymapKeyTypedDict]]

class ListComponentTypedDict(TypedDict):
    subcomponent: Required[str|None]
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    ordered: NotRequired[bool]
    print_all: NotRequired[bool]
    print_flat: NotRequired[bool]
    type: Required[Literal["List"]]
    types: Required[list[str]]

class NbtBaseTypedDict(TypedDict):
    subcomponent: Required[str]
    endianness: Required[Literal["big", "little"]]
    normalizer: NotRequired[list[str]|str]
    type: Required[Literal["NbtBase"]]
    types: Required[list[str]]

class NormalizerTypedDict(TypedDict):
    dependencies: Required[list[str]]
    function_name: Required[str]
    type: Required[Literal["Normalizer"]]

class TagTypedDict(TypedDict):
    type: Required[Literal["Tag"]]

class TypeAliasTypedDict(TypedDict):
    type: Required[Literal["TypeAlias"]]
    types: Required[list[str]]

class VolumeTypedDict(TypedDict):
    field: NotRequired[str]
    normalizer: NotRequired[str|list[str]]
    position_key: Required[str]
    print_additional_data: NotRequired[bool]
    state_key: Required[str]
    subcomponent: Required[str|None]
    tags: NotRequired[list[str]]
    this_type: Required[str]
    type: Required[Literal["Volume"]]
    types: Required[list[str]]

ComponentTypedDicts = BaseComponentTypedDict|DictComponentTypedDict|GroupComponentTypedDict|KeymapComponentTypedDict|ListComponentTypedDict|NbtBaseTypedDict|NormalizerTypedDict|TypeAliasTypedDict|VolumeTypedDict
StructureComponentTypedDicts = DictComponentTypedDict|KeymapComponentTypedDict|ListComponentTypedDict|VolumeTypedDict
StructureFileType = dict[str,ComponentTypedDicts]

DEFAULT_TYPES:dict[str,type] = {
    "bool": bool,
    "dict": dict,
    "float": float,
    "int": int,
    "list": list,
    "null": type(None),
    "str": str,
    "volume_base": tuple, # Volume becomes a tuple with various contents upon being normalized
    "nbt_base": NbtReader.NbtBytes,
    "TAG_Byte": NbtTypes.TAG_Byte,
    "TAG_Short": NbtTypes.TAG_Short,
    "TAG_Int": NbtTypes.TAG_Int,
    "TAG_Long": NbtTypes.TAG_Long,
    "TAG_Float": NbtTypes.TAG_Float,
    "TAG_Double": NbtTypes.TAG_Double,
    "TAG_Byte_Array": NbtTypes.TAG_Byte_Array,
    "TAG_String": NbtTypes.TAG_String,
    "TAG_List": NbtTypes.TAG_List,
    "TAG_Compound": NbtTypes.TAG_Compound,
    "TAG_Int_Array": NbtTypes.TAG_Int_Array,
    "TAG_Long_Array": NbtTypes.TAG_Long_Array,
}
REQUIRES_SUBCOMPONENT_TYPES = set([dict, list, NbtTypes.TAG_Byte_Array, NbtTypes.TAG_List, NbtTypes.TAG_Compound, NbtTypes.TAG_Int_Array, NbtTypes.TAG_Long_Array])
