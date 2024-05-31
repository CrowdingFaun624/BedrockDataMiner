from typing import Any, Literal, TypeAlias, TypedDict, Union, overload

from typing_extensions import NotRequired, Required

import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class DictTypedDict(TypedDict):
    type: Required[Literal["Dict"]]
    data_type: Required[str|list[str]]
    data_type_str: Required[str]
    key_type: Required[Union[str, list[str], "TypedVerifierTypedDicts"]]
    key_type_str: Required[str]
    value_type: Required[Union[str, list[str], "TypedVerifierTypedDicts"]]
    value_type_str: Required[str]

class TypedDictKeyTypedDict(TypedDict):
    required: Required[bool]
    value_str: Required[str]
    value_type: Required[Union[str, list[str], "TypedVerifierTypedDicts"]]

class TypedDictTypedDict(TypedDict):
    type: Required[Literal["TypedDict"]]
    data_type: NotRequired[str|list[str]]
    data_type_str: NotRequired[str]
    keys: Required[dict[str,TypedDictKeyTypedDict]]

class ListTypedDict(TypedDict):
    type: Required[Literal["List"]]
    data_type: Required[str|list[str]]
    data_type_str: Required[str]
    item_type: Required[Union[str, list[str], "TypedVerifierTypedDicts"]]
    item_type_str: Required[str]

class TupleItemTypedDict(TypedDict):
    item_type: Required[Union[str, list[str], "TypedVerifierTypedDicts"]]
    item_type_str: str

class TupleTypedDict(TypedDict):
    type: Required[Literal["Tuple"]]
    data_type: Required[str|list[str]]
    data_type_str: Required[str]
    items: Required[list[TupleItemTypedDict]]

class EnumTypedDict(TypedDict):
    type: Required[Literal["Enum"]]
    options: Required[list[Any]]

class UnionTypedDict(TypedDict):
    type: Required[Literal["Union"]]
    type_str: Required[str]
    types: Required[list[Union[str, "TypedVerifierTypedDicts"]]]

TypedVerifierTypedDicts:TypeAlias = DictTypedDict|TypedDictTypedDict|ListTypedDict|TupleTypedDict|EnumTypedDict|UnionTypedDict

allowed_types = {
    "bool": bool, 
    "dict": dict, 
    "float": float, 
    "int": int, 
    "list": list, 
    "null": type(None), 
    "str": str, 
    "tuple": tuple
}

@overload
def parse_type_field(data:str|list[str], allow_type_verifier:Literal[False]) -> type|tuple[type]: ...
@overload
def parse_type_field(data:str|list[str]|TypedVerifierTypedDicts, allow_type_verifier:Literal[True]) -> type|tuple[type]|TypeVerifier.TypeVerifier: ...
def parse_type_field(data:str|list[str]|TypedVerifierTypedDicts, allow_type_verifier:bool) -> type|tuple[type]|TypeVerifier.TypeVerifier:
    if isinstance(data, str):
        return allowed_types[data]
    elif isinstance(data, list):
        return tuple(allowed_types[type_str] for type_str in data)
    else:
        if not allow_type_verifier:
            raise TypeError("TypeVerifier is not allowed here!")
        return parse_type_verifier(data)

def parse_dict(data:DictTypedDict) -> TypeVerifier.DictTypeVerifier:
    return TypeVerifier.DictTypeVerifier(
        data_type=parse_type_field(data["data_type"], allow_type_verifier=False),
        key_type=parse_type_field(data["key_type"], allow_type_verifier=True),
        value_type=parse_type_field(data["value_type"], allow_type_verifier=True),
        data_type_str=data["data_type_str"],
        key_type_str=data["key_type_str"],
        value_type_str=data["value_type_str"],
    )

def parse_enum(data:EnumTypedDict) -> TypeVerifier.EnumTypeVerifier:
    return TypeVerifier.EnumTypeVerifier(
        options=data["options"],
    )

def parse_list(data:ListTypedDict) -> TypeVerifier.ListTypeVerifier:
    return TypeVerifier.ListTypeVerifier(
        item_type=parse_type_field(data["item_type"], allow_type_verifier=True),
        data_type=parse_type_field(data["data_type"], allow_type_verifier=False),
        item_type_str=data["item_type_str"],
        data_type_str=data["data_type_str"],
    )

def parse_tuple(data:TupleTypedDict) -> TypeVerifier.TupleTypeVerifier:
    return TypeVerifier.TupleTypeVerifier(
        *(TypeVerifier.TupleItemTypeVerifier(
            item_type=parse_type_field(item["item_type"], allow_type_verifier=True),
            item_type_str=item["item_type_str"],
        ) for item in data["items"]),
        data_type=parse_type_field(data["data_type"], allow_type_verifier=False),
        data_type_str=data["data_type_str"],
    )

def parse_typed_dict(data:TypedDictTypedDict) -> TypeVerifier.TypedDictTypeVerifier:
    return TypeVerifier.TypedDictTypeVerifier(
        *(TypeVerifier.TypedDictKeyTypeVerifier(
            key=key,
            value_str=value["value_str"],
            required=value["required"],
            value_type=parse_type_field(value["value_type"], allow_type_verifier=True),
        ) for key, value in data["keys"].items()),
        data_type=parse_type_field(data.get("data_type", "dict"), allow_type_verifier=False),
        data_type_str=data.get("data_type_str", "a dict"),
    )

def parse_union(data:UnionTypedDict) -> TypeVerifier.UnionTypeVerifier:
    return TypeVerifier.UnionTypeVerifier(
        data["type_str"],
        (parse_type_field(item, allow_type_verifier=True) for item in data["types"]),
    )

def parse_type_verifier(data:TypedVerifierTypedDicts) -> TypeVerifier.TypeVerifier:
    match data["type"]:
        case "Dict":
            return parse_dict(data)
        case "Enum":
            return parse_enum(data)
        case "List":
            return parse_list(data)
        case "Tuple":
            return parse_tuple(data)
        case "TypedDict":
            return parse_typed_dict(data)
        case "Union":
            return parse_union(data)

def main() -> None:
    type_verifier = parse_type_verifier({
        "type": "TypedDict",
        "keys": {
            "wow": {"required": True, "value_str": "an int", "value_type": "int"},
        },
    })
    type_verifier.base_verify({"wow": 42})
