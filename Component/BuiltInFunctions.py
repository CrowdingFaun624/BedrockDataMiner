import json
from types import EllipsisType
from typing import TYPE_CHECKING, Any, Callable, Sized

from Component.ComponentFunctions import register_builtin
from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.SimpleContainer import SCon
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

type sort_item = tuple[Con|Don|Diff[Don], Con|Don|Diff[Don]]
type key_function = Callable[["SupportsRichComparison"], str]
type sort_inner_function = Callable[[sort_item],"SupportsRichComparison"]
type sort_function = Callable[[key_function, dict[str,int]], sort_inner_function]

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key", True, str),
))
def delete_key(data:dict[str,Any], key:str) -> dict[str,Any]:
    return {_key: value for _key, value in data.items() if _key != key}

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("keys", True, ListTypeVerifier(str, list)),
))
def delete_keys(data:dict[str,Any], keys:list[str]) -> dict[str,Any]:
    return {_key: value for _key, value in data.items() if _key not in keys}

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key", True, str),
))
def delete_key_if_empty(data:dict[str,Sized], key:str) -> dict[str,Sized]:
    return {_key: value for _key, value in data.items() if _key != key or len(value) == 0}

@register_builtin(no_arguments=True)
def identity[A](data:A) -> A:
    return data

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key", True, str)
))
def get_key[A](data:dict[str,A], key:str) -> A:
    return data[key]

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key", True, str),
    TypedDictKeyTypeVerifier("default", True, object),
))
def get_get_key[A](data:dict[str,A], key:str, default:A) -> A:
    return data.get(key, default)

@register_builtin(no_arguments=True)
def load_json(data:str) -> dict[str,str]:
    return json.loads(data)

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key_function", True, object),
    TypedDictKeyTypeVerifier("keys_order", True, DictTypeVerifier(dict, str, int)),
))
def sort_by_component_order(key_function:key_function, keys_order:dict[str,int]) -> sort_inner_function:
    def sort(item:sort_item) -> "SupportsRichComparison":
        key, value = item
        match key:
            case Con():
                return keys_order.get(key_function(key.data), 0)
            case Don():
                return keys_order.get(key_function(key.last_value), 0)
            case Diff():
                return keys_order.get(key_function(key.last_value.last_value), 0)
    return sort

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key_function", True, object),
    TypedDictKeyTypeVerifier("keys_order", True, DictTypeVerifier(dict, str, int)),
))
def sort_by_key(key_function:key_function, keys_order:dict[str,int]) -> sort_inner_function:
    def sort(item:sort_item) -> "SupportsRichComparison":
        key, value = item
        match key:
            case Con():
                return key.data
            case Don():
                return key.last_value
            case Diff():
                return key.last_value.last_value
    return sort

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key_function", True, object),
    TypedDictKeyTypeVerifier("keys_order", True, DictTypeVerifier(dict, str, int)),
))
def sort_by_value(key_function:key_function, keys_order:dict[str,int]) -> sort_inner_function:
    def sort(item:sort_item) -> "SupportsRichComparison":
        key, value = item
        match value:
            case Con():
                return value.data
            case Don():
                return value.last_value
            case Diff():
                return value.last_value.last_value
    return sort

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key", True, str),
    TypedDictKeyTypeVerifier("delete", False, bool),
))
def wrap_in_dict(data:list[dict[str,Any]], key:str, delete:bool=False) -> dict[str,dict[str,Any]]:
    if delete:
        return {item[key]: {_key: _value for _key, _value in item.items() if _key != key} for item in data}
    else:
        return {item[key]: item for item in data}

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key_key", True, str),
    TypedDictKeyTypeVerifier("value_key", True, str),
    TypedDictKeyTypeVerifier("default", False, object),
))
def turn_to_dict(data:list[dict[str,Any]], key_key:str, value_key:str, default:Any|EllipsisType=...) -> dict[str,Any]:
    output:dict[str,Any] = {}
    for item in data:
        assert len(item) in ((2,) if default is ... else (1, 2))
        output[item[key_key]] = item.get(value_key, default) if default is not ... else item[value_key]
    return output

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("keys", True, ListTypeVerifier(str, list)),
))
def wrap_tuple(data:list[Any], keys:list[str]) -> dict[str,Any]:
    return {key: value for key, value in zip(keys, data, strict=True)}

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("from_key", True, str),
    TypedDictKeyTypeVerifier("to_key", True, str),
))
def move_key(data:dict[str,Any], from_key:str, to_key:str) -> dict[str,Any]:
    if from_key in data:
        if to_key in data:
            raise KeyError(f"Attempted to move \"{from_key}\" to \"{to_key}\", but \"{to_key}\" already exists!")
        output = data.copy()
        output[to_key] = output[from_key]
        del output[from_key]
        return output
    else:
        return data

@register_builtin(no_arguments=True)
def parse_int(data:str) -> int:
    return int(data)

@register_builtin(no_arguments=True)
def parse_float(data:str) -> float:
    return float(data)

@register_builtin(no_arguments=True)
def parse_number(data:str) -> int|float:
    try:
        return int(data)
    except Exception:
        return float(data)

@register_builtin(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("keep_ends", False, bool),
))
def split_lines(data:str, keep_ends:bool=False) -> list[str]:
    return data.splitlines(keep_ends)

@register_builtin(no_arguments=True)
def get_file_stem(data:SCon[str]) -> str:
    return data.data.split("/")[-1].split(".", 1)[0]
