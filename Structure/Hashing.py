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

class HashTableItem():

    def __new__(cls, function:Callable[[d],int], type_form:type[d]) -> Callable[[d],int]:
        return function

hash_type_table:dict[type,Callable] = { # I will have type hinting no matter how weird
    bool: HashTableItem(lambda data: hash(data), bool),
    bytearray: HashTableItem(lambda data: hash(tuple(item for item in data)), bytearray),
    bytes: HashTableItem(lambda data: hash(data), bytes),
    complex: HashTableItem(lambda data: hash(data), complex),
    D.Diff: HashTableItem(lambda data: hash((hash_data(data.old), hash_data(data.new))), D.Diff),
    D.NoExist: HashTableItem(lambda data: hash(data), D.NoExist),
    dict: HashTableItem(lambda data: hash(tuple((hash(key), hash_data(value)) for key, value in data.items())), dict),
    float: HashTableItem(lambda data: hash(data), float),
    frozenset: HashTableItem(lambda data: hash(tuple(item for item in data)), frozenset),
    int: HashTableItem(lambda data: hash(data), int),
    list: HashTableItem(lambda data: hash(tuple(hash_data(item) for item in data)), list),
    memoryview: HashTableItem(lambda data: hash(data), memoryview),
    NbtReader.NbtBytes: HashTableItem(lambda data: hash(data), NbtReader.NbtBytes),
    NbtTypes.TAG_Byte: HashTableItem(lambda data: hash(data), NbtTypes.TAG_Byte),
    NbtTypes.TAG_End: HashTableItem(lambda data: hash(data), NbtTypes.TAG_End),
    NbtTypes.TAG_Short: HashTableItem(lambda data: hash(data), NbtTypes.TAG_Short),
    NbtTypes.TAG_Int: HashTableItem(lambda data: hash(data), NbtTypes.TAG_Int),
    NbtTypes.TAG_Long: HashTableItem(lambda data: hash(data), NbtTypes.TAG_Long),
    NbtTypes.TAG_Float: HashTableItem(lambda data: hash(data), NbtTypes.TAG_Float),
    NbtTypes.TAG_Double: HashTableItem(lambda data: hash(data), NbtTypes.TAG_Double),
    NbtTypes.TAG_Byte_Array: HashTableItem(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_Byte_Array),
    NbtTypes.TAG_String: HashTableItem(lambda data: hash(data), NbtTypes.TAG_String),
    NbtTypes.TAG_List: HashTableItem(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_List),
    NbtTypes.TAG_Compound: HashTableItem(lambda data: hash(tuple((hash(key), hash_data(value)) for key, value in data.items())), NbtTypes.TAG_Compound),
    NbtTypes.TAG_Int_Array: HashTableItem(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_Int_Array),
    NbtTypes.TAG_Long_Array: HashTableItem(lambda data: hash(tuple(hash_data(item) for item in data)), NbtTypes.TAG_Long_Array),
    type(None): HashTableItem(lambda data: hash(data), type(None)),
    range: HashTableItem(lambda data: hash(data), range),
    set: HashTableItem(lambda data: hash(tuple(item for item in data)), set),
    str: HashTableItem(lambda data: hash(data), str),
    tuple: HashTableItem(lambda data: hash(tuple(hash_data(item) for item in data)), tuple),
}
