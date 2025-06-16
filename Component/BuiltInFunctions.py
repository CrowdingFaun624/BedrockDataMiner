import json
from typing import TYPE_CHECKING, Any, Callable, Sized

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.SimpleContainer import SCon

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

type sort_item = tuple[Con|Don|Diff[Don], Con|Don|Diff[Don]]
type key_function = Callable[["SupportsRichComparison"], str]
type sort_inner_function = Callable[[sort_item],"SupportsRichComparison"]
type sort_function = Callable[[key_function, dict[str,int]], sort_inner_function]

def delete_required_key(data:dict[str,Any], key:str) -> None:
    del data[key]

def delete_optional_key(data:dict[str,Any], key:str) -> None:
    data.pop(key, None)

def delete_required_keys(data:dict[str,Any], keys:list[str]) -> None:
    for key in keys:
        del data[key]

def delete_optional_keys(data:dict[str,Any], keys:list[str]) -> None:
    for key in keys:
        data.pop(key, None)

def delete_key_if_empty(data:dict[str,Sized], key:str) -> None:
    if (value := data.get(key)) is not None and len(value) == 0:
        data.pop(key, None)

def identity[A](data:A) -> A:
    return data

def get_key[A](data:dict[str,A], key:str) -> A:
    return data[key]

def load_json(data:str) -> dict[str,str]:
    return json.loads(data)

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

def wrap_in_dict(data:list[dict[str,Any]], key:str, delete:bool=False) -> dict[str,dict[str,Any]]:
    output = {item[key]: item for item in data}
    if delete:
        for value in output.values():
            del value[key]
    return output

def wrap_in_value(data:dict[str,Any], key:str, delete:bool=False) -> dict[str,dict[str,Any]]:
    value = data[key]
    if delete:
        del value[key]
    return {value: data}

def turn_to_dict(data:list[dict[str,Any]], key_key:str, value_key:str) -> dict[str,Any]:
    output:dict[str,Any] = {}
    for item in data:
        assert len(item) == 2
        output[item[key_key]] = item[value_key]
    return output

def wrap_tuple(data:list[Any], keys:list[str]) -> dict[str,Any]:
    assert len(data) == len(keys)
    return {key: value for key, value in zip(keys, data)}

def move_key(data:dict[str,Any], from_key:str, to_key:str) -> None:
    if from_key in data:
        if to_key in data:
            raise KeyError(f"Attempted to move \"{from_key}\" to \"{to_key}\", but \"{to_key}\" already exists!")
        data[to_key] = data[from_key]
        del data[from_key]

def parse_int(data:str) -> int:
    return int(data)

def parse_float(data:str) -> float:
    return float(data)

def parse_number(data:str) -> int|float:
    try:
        return int(data)
    except Exception:
        return float(data)

def split_lines(data:str, keep_ends:bool=False) -> list[str]:
    return data.splitlines(keep_ends)

def get_file_stem(data:SCon[str]) -> str:
    return data.data.split("/")[-1].split(".", 1)[0]

built_in_functions:dict[str,Callable] = {
    "delete_key_if_empty": delete_key_if_empty,
    "delete_optional_key": delete_optional_key,
    "delete_optional_keys": delete_optional_keys,
    "delete_required_key": delete_required_key,
    "delete_required_keys": delete_required_keys,
    "get_file_stem": get_file_stem,
    "get_key": get_key,
    "identity": identity,
    "load_json": load_json,
    "move_key": move_key,
    "parse_float": parse_float,
    "parse_int": parse_int,
    "parse_number": parse_number,
    "sort_by_component_order": sort_by_component_order,
    "sort_by_key": sort_by_key,
    "sort_by_value": sort_by_value,
    "split_lines": split_lines,
    "turn_to_dict": turn_to_dict,
    "wrap_in_dict": wrap_in_dict,
    "wrap_in_value": wrap_in_value,
    "wrap_tuple": wrap_tuple,
}

