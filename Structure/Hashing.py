from typing import Any, Callable, TypeVar

import Structure.Difference as D
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes

def hash_data(data:Any) -> int:
    '''
    Tries its best to hash anything, including mutable objects. Will throw an exception if it can't figure out how.
    :data: The data to hash
    '''
    hash_function = hash_type_table.get(type(data))
    if hash_function is not None:
        return hash_function(data)
    else:
        raise Exceptions.CacheStructureHashError(data.__class__)

d = TypeVar("d")

def hash_table_item(function:Callable[[d],int], type_form:type[d]) -> Callable[[d],int]:
    return function

hash_type_table:dict[type,Callable] = { # I will have type hinting no matter how weird
    bool: hash_table_item(lambda data: hash(data), bool),
    bytearray: hash_table_item(lambda data: hash(tuple(item for item in data)), bytearray),
    bytes: hash_table_item(lambda data: hash(data), bytes),
    complex: hash_table_item(lambda data: hash(data), complex),
    D.Diff: hash_table_item(lambda data: hash((hash_data(data.old), hash_data(data.new))), D.Diff),
    D.NoExist: hash_table_item(lambda data: hash(data), D.NoExist),
    dict: hash_table_item(lambda data: hash(tuple((hash(key), hash_data(value)) for key, value in data.items())), dict),
    float: hash_table_item(lambda data: hash(data), float),
    frozenset: hash_table_item(lambda data: hash(tuple(item for item in data)), frozenset),
    int: hash_table_item(lambda data: hash(data), int),
    list: hash_table_item(lambda data: hash(tuple(hash_data(item) for item in data)), list),
    memoryview: hash_table_item(lambda data: hash(data), memoryview),
    NbtReader.NbtBytes: hash_table_item(lambda data: hash(data), NbtReader.NbtBytes),
    NbtTypes.TAG_Byte: hash_table_item(lambda data: hash(data), NbtTypes.TAG_Byte),
    NbtTypes.TAG_End: hash_table_item(lambda data: hash(data), NbtTypes.TAG_End),
    NbtTypes.TAG_Short: hash_table_item(lambda data: hash(data), NbtTypes.TAG_Short),
    NbtTypes.TAG_Int: hash_table_item(lambda data: hash(data), NbtTypes.TAG_Int),
    NbtTypes.TAG_Long: hash_table_item(lambda data: hash(data), NbtTypes.TAG_Long),
    NbtTypes.TAG_Float: hash_table_item(lambda data: hash(data), NbtTypes.TAG_Float),
    NbtTypes.TAG_Double: hash_table_item(lambda data: hash(data), NbtTypes.TAG_Double),
    NbtTypes.TAG_Byte_Array: hash_table_item(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_Byte_Array),
    NbtTypes.TAG_String: hash_table_item(lambda data: hash(data), NbtTypes.TAG_String),
    NbtTypes.TAG_List: hash_table_item(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_List),
    NbtTypes.TAG_Compound: hash_table_item(lambda data: hash(tuple((hash(key), hash_data(value)) for key, value in data.items())), NbtTypes.TAG_Compound),
    NbtTypes.TAG_Int_Array: hash_table_item(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_Int_Array),
    NbtTypes.TAG_Long_Array: hash_table_item(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_Long_Array),
    type(None): hash_table_item(lambda data: hash(data), type(None)),
    range: hash_table_item(lambda data: hash(data), range),
    set: hash_table_item(lambda data: hash(tuple(item for item in data)), set),
    str: hash_table_item(lambda data: hash(data), str),
    tuple: hash_table_item(lambda data: hash(tuple(hash_data(item) for item in data)), tuple),
}
