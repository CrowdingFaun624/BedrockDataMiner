import json
from typing import Any, Callable, TypeVar

import Utilities.File as File

a = TypeVar("a")

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

def load_json(data:str) -> dict[str,str]:
    return json.loads(data)

def wrap_in_dict(data:list[dict[str,Any]], key:str, delete:bool=False) -> dict[str,dict[str,Any]]:
    output = {item[key]: item for item in data}
    if delete:
        for value in output.values():
            del value[key]
    return output

def wrap_tuple(data:list[Any], keys:list[str]) -> dict[str,Any]:
    assert len(data) == len(keys)
    return {key: value for key, value in zip(keys, data)}

def move_key(data:dict[str,Any], from_key:str, to_key:str) -> None:
    if from_key in data:
        if to_key in data:
            raise KeyError("Attempted to move \"%s\" to \"%s\", but \"%s\" already exists!" % (from_key, to_key, to_key))
        data[to_key] = data[from_key]
        del data[from_key]

def open_file(data:File.File[a]) -> a:
    return data.read()

functions:dict[str,Callable] = {
    "delete_optional_key": delete_optional_key,
    "delete_optional_keys": delete_optional_keys,
    "delete_required_key": delete_required_key,
    "delete_required_keys": delete_required_keys,
    "load_json": load_json,
    "move_key": move_key,
    "open_file": open_file,
    "wrap_in_dict": wrap_in_dict,
    "wrap_tuple": wrap_tuple,
}
