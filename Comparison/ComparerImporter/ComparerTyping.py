from typing import Literal, TYPE_CHECKING, TypedDict, TypeVar, Union
from typing_extensions import NotRequired, Required

if TYPE_CHECKING:
    import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
    import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
    import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate

class DictComparerTypedDict(TypedDict):
    comparer: Required[str|None]
    comparison_move_function: NotRequired[str]
    detect_key_moves: NotRequired[bool]
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    type: Required[Literal["Dict"]]
    print_all: NotRequired[bool]
    types: Required[list[str]]

class GroupTypedDict(TypedDict):
    type: Required[Literal["Group"]]
    types: Required[dict[str,str|None]]

class ListComparerTypedDict(TypedDict):
    comparer: Required[str|None]
    field: NotRequired[str]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str|list[str]]
    ordered: NotRequired[bool]
    print_all: NotRequired[bool]
    print_flat: NotRequired[bool]
    type: Required[Literal["List"]]
    types: Required[list[str]]

ComponentTypedDict = TypedDict("ComponentTypedDict", {"as": NotRequired[str], "component": Required[str]})

ImportTypedDict = TypedDict("ImportTypedDict", {"from": Required[str], "components": Required[list[ComponentTypedDict]]})

class MainTypedDict(TypedDict):
    base_comparer_section: Required[str]
    imports: NotRequired[list[ImportTypedDict]]
    name: Required[str]
    normalizer: NotRequired[str]
    post_normalizer: NotRequired[str]
    type: Required[Literal["Main"]]

class NbtBaseTypedDict(TypedDict):
    comparer: Required[str]
    type: Required[Literal["NbtBase"]]

class NormalizerFunctionTypedDict(TypedDict):
    dependencies: Required[list[str]]
    function_name: Required[str]
    type: Required[Literal["NormalizerFunction"]]

class TypeAliasTypedDict(TypedDict):
    type: Required[Literal["TypeAlias"]]
    types: Required[list[str]]

class TypedDictTypeTypedDict(TypedDict):
    type: Required[str|list[str]]
    comparer: NotRequired[str|None]
    tags: NotRequired[list[str]]

class TypedDictTypeFilledTypedDict(TypedDict):
    type: Required[list[Union[type, "TypeAliasIntermediate.TypeAliasIntermediate"]]]
    comparer: Required[Union["ComparerIntermediate.ComparerIntermediate", "GroupIntermediate.GroupIntermediate", None]]
    tags: NotRequired[list[str]]

class TypedDictComparerTypedDict(TypedDict):
    field: NotRequired[str]
    imports: NotRequired[str|list[str]]
    measure_length: NotRequired[bool]
    normalizer: NotRequired[str]
    type: Required[Literal["TypedDict"]]
    types: Required[dict[str,TypedDictTypeTypedDict]]

Intermediates = DictComparerTypedDict|GroupTypedDict|ListComparerTypedDict|MainTypedDict|NormalizerFunctionTypedDict|TypeAliasTypedDict|TypedDictComparerTypedDict
Comparers = DictComparerTypedDict|ListComparerTypedDict|TypedDictComparerTypedDict
ComparerType = dict[str,Intermediates]

DEFAULT_TYPES:dict[str,type] = {"bool": bool, "dict": dict, "float": float, "int": int, "list": list, "null": type(None), "str": str}
REQUIRES_COMPARER_TYPES = set([dict, list])

IntermediateType = TypeVar("IntermediateType", DictComparerTypedDict, GroupTypedDict, ListComparerTypedDict, MainTypedDict, NormalizerFunctionTypedDict, TypeAliasTypedDict, TypedDictComparerTypedDict)
ComparerGeneric = TypeVar("ComparerGeneric", DictComparerTypedDict, ListComparerTypedDict, TypedDictComparerTypedDict)
ChooseIntermediateType = TypeVar("ChooseIntermediateType", DictComparerTypedDict, GroupTypedDict, ListComparerTypedDict, MainTypedDict, NormalizerFunctionTypedDict, TypeAliasTypedDict, TypedDictComparerTypedDict)