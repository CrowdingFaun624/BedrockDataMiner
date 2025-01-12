import json
from typing import Any, Callable, Sized

import Utilities.File as File


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

def get_key[A](data:dict[str,A], key:str) -> A:
    return data[key]

def load_json(data:str) -> dict[str,str]:
    return json.loads(data)

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

def open_file[a](data:File.AbstractFile[a]) -> a:
    return data.data

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

def get_file_stem(data:str) -> str:
    return data.split("/")[-1].split(".", 1)[0]

functions:dict[str,Callable] = {
    "delete_key_if_empty": delete_key_if_empty,
    "delete_optional_key": delete_optional_key,
    "delete_optional_keys": delete_optional_keys,
    "delete_required_key": delete_required_key,
    "delete_required_keys": delete_required_keys,
    "get_file_stem": get_file_stem,
    "get_key": get_key,
    "load_json": load_json,
    "move_key": move_key,
    "open_file": open_file,
    "parse_float": parse_float,
    "parse_int": parse_int,
    "parse_number": parse_number,
    "split_lines": split_lines,
    "turn_to_dict": turn_to_dict,
    "wrap_in_dict": wrap_in_dict,
    "wrap_in_value": wrap_in_value,
    "wrap_tuple": wrap_tuple,
}
