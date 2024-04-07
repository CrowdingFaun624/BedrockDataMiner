from typing import Literal, TYPE_CHECKING, TypedDict, Union
from typing_extensions import NotRequired, Required

import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.Nbt.NbtReader as NbtReader

if TYPE_CHECKING:
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Importer.GroupComponent as GroupComponent
    import Structure.Importer.TypeAliasComponent as TypeAliasComponent

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

ImportedComponentTypedDict = TypedDict("ImportedComponentTypedDict", {"as": NotRequired[str], "component": Required[str]})

ImportTypedDict = TypedDict("ImportTypedDict", {"from": Required[str], "components": Required[list[ImportedComponentTypedDict]]})

class BaseComponentTypedDict(TypedDict):
    subcomponent: Required[str]
    imports: NotRequired[list[ImportTypedDict]]
    name: Required[str]
    normalizer: NotRequired[str]
    post_normalizer: NotRequired[str]
    type: Required[Literal["Base"]]

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

class TypeAliasTypedDict(TypedDict):
    type: Required[Literal["TypeAlias"]]
    types: Required[list[str]]

class KeymapKeyTypedDict(TypedDict):
    type: Required[str|list[str]]
    subcomponent: NotRequired[str|None]
    tags: NotRequired[list[str]]

class KeymapKeyFilledTypedDict(TypedDict):
    type: Required[list[Union[type, "TypeAliasComponent.TypeAliasComponent"]]]
    subcomponent: Required[Union["StructureComponent.StructureComponent", "GroupComponent.GroupComponent", None]]
    tags: NotRequired[list[str]]

class KeymapComponentTypedDict(TypedDict):
    field: NotRequired[str]
    imports: NotRequired[str|list[str]]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    type: Required[Literal["Keymap"]]
    keys: Required[dict[str,KeymapKeyTypedDict]]

ComponentTypedDicts = DictComponentTypedDict|GroupComponentTypedDict|ListComponentTypedDict|BaseComponentTypedDict|NbtBaseTypedDict|NormalizerTypedDict|TypeAliasTypedDict|KeymapComponentTypedDict
StructureComponentTypedDicts = DictComponentTypedDict|ListComponentTypedDict|KeymapComponentTypedDict
StructureFileType = dict[str,ComponentTypedDicts]

DEFAULT_TYPES:dict[str,type] = {
    "bool": bool,
    "dict": dict,
    "float": float,
    "int": int,
    "list": list,
    "null": type(None),
    "str": str,
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
