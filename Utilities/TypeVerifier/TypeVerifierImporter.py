import traceback
from typing import (Any, Literal, NotRequired, Required, TypedDict, Union,
                    cast, overload)

import Utilities.Exceptions as Exceptions
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
    loose: NotRequired[bool]

class ListTypedDict(TypedDict):
    type: Required[Literal["List"]]
    data_type: Required[str|list[str]]
    data_type_str: Required[str]
    item_type: Required[Union[str, list[str], "TypedVerifierTypedDicts"]]
    item_type_str: Required[str]

class TupleItemTypedDict(TypedDict):
    item_type: Required[Union[str, list[str], "TypedVerifierTypedDicts"]]
    item_type_str: Required[str]

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

type TypedVerifierTypedDicts = DictTypedDict|TypedDictTypedDict|ListTypedDict|TupleTypedDict|EnumTypedDict|UnionTypedDict

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


def type_verify_type_verifier(key:str, value:TypedVerifierTypedDicts) -> tuple[bool,str]:
    if not isinstance(value, dict):
        return False, "Data is not a dict!"
    elif "type" not in value:
        return False, "Key \"type\" is not in data!"
    trace = TypeVerifier.Trace()
    match value["type"]:
        case "Dict":
            exceptions = dict_type_verifier.verify(value, trace)
        case "Enum":
            exceptions = enum_type_verifier.verify(value, trace)
        case "List":
            exceptions = list_type_verifier.verify(value, trace)
        case "Tuple":
            exceptions = tuple_type_verifier.verify(value, trace)
        case "TypedDict":
            exceptions = typed_dict_type_verifier.verify(value, trace)
        case "Union":
            exceptions = union_type_verifier.verify(value, trace)
        case _:
            return False, "Unknown TypeVerifier type \"%s\"!" % value["type"]
    if len(exceptions) > 0:
        return False, "\n".join("\n".join("\t" + exception_line for exception_line in traceback.format_exception(exception)) for exception in exceptions)
    else:
        return True, ""

dict_type_verifier = TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier(("Dict",))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type_str", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("key_type", "a str, list, or TypeVerifier", True, TypeVerifier.UnionTypeVerifier("a str, list, or TypeVerifier", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")), function=lambda key, value: ((True, "") if not isinstance(value, dict) else type_verify_type_verifier(key, cast(TypedVerifierTypedDicts, value)))),
    TypeVerifier.TypedDictKeyTypeVerifier("key_type_str", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("value_type", "a str, list, or TypeVerifier", True, TypeVerifier.UnionTypeVerifier("a str, list, or TypeVerifier", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")), function=lambda key, value: ((True, "") if not isinstance(value, dict) else type_verify_type_verifier(key, cast(TypedVerifierTypedDicts, value)))),
    TypeVerifier.TypedDictKeyTypeVerifier("value_type_str", "a str", True, str),
)

typed_dict_type_verifier = TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier(("TypedDict",))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type_str", "a str", False, str),
    TypeVerifier.TypedDictKeyTypeVerifier("keys", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("required", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("value_str", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("value_type", "a str, list, or TypeVerifier", True, TypeVerifier.UnionTypeVerifier("a str or list", str, dict, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        function=lambda data: type_verify_type_verifier("", cast(TypedVerifierTypedDicts, data["value_type"])) if isinstance(data.get("value_type", None), dict) else (True, "")
    ), "a dict", "a str", "a dict")),
    TypeVerifier.TypedDictKeyTypeVerifier("loose", "a bool", False, bool),
)

list_type_verifier = TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier(("List",))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type_str", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("item_type", "a str, list, or TypeVerifier", True, TypeVerifier.UnionTypeVerifier("a str, list, or TypeVerifier", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")), function=lambda key, value: ((True, "") if not isinstance(value, dict) else type_verify_type_verifier(key, cast(TypedVerifierTypedDicts, value)))),
    TypeVerifier.TypedDictKeyTypeVerifier("item_type_str", "a str", True, str),
)

tuple_type_verifier = TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier(("Tuple",))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    TypeVerifier.TypedDictKeyTypeVerifier("data_type_str", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("items", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("item_type", "a str, list, or TypeVerifier", True, TypeVerifier.UnionTypeVerifier("a str, list, or TypeVerifier", str, dict, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")), function=lambda key, value: ((True, "") if not isinstance(value, dict) else type_verify_type_verifier(key, cast(TypedVerifierTypedDicts, value)))),
        TypeVerifier.TypedDictKeyTypeVerifier("item_type_str", "a str", True, str),
    ), list, "a dict", "a list"))
)

enum_type_verifier = TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier(("Enum",))),
    TypeVerifier.TypedDictKeyTypeVerifier("options", "a list", True, TypeVerifier.ListTypeVerifier(object, list, "an object", "a list")),
)

union_type_verifier = TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier(("Union",))),
    TypeVerifier.TypedDictKeyTypeVerifier("type_str", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.UnionTypeVerifier("a str or TypeVerifier", str, dict), list, "a str or TypeVerifier", "a list", item_function=lambda item: ((True, "") if not isinstance(item, dict) else type_verify_type_verifier("", cast(TypedVerifierTypedDicts, item))))),
)

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
            raise Exceptions.TypeVerifierDisallowedError(data)
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
        loose=data.get("loose", False)
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
