from collections import defaultdict
from typing import Any, Callable

import Utilities.CustomJson as CustomJson
import Utilities.TypeUtilities as TypeUtilities


class NoCoder():
    '''
    Used to annotate that a type specifically has no JSON Coder.
    '''
    # does nothing otherwise.
    ...

no_coder = NoCoder()

default_types:dict[str,type] = {}
requires_subcomponent_types = TypeUtilities.TypeSet()
sortable_types = TypeUtilities.TypeSet()
mutually_sortable:defaultdict[str,TypeUtilities.TypeSet] = defaultdict(lambda: TypeUtilities.TypeSet())
file_types = TypeUtilities.TypeSet()
iterable_types = TypeUtilities.TypeSet()
mapping_types = TypeUtilities.TypeSet()
string_types = TypeUtilities.TypeSet()
containment_types:TypeUtilities.TypeDict[object, TypeUtilities.TypeSet] = TypeUtilities.TypeDict()
hash_type_table:TypeUtilities.TypeDict[Any,Callable[[Any],int]] = TypeUtilities.TypeDict()
json_encoders:TypeUtilities.TypeDict[object, type[CustomJson.Coder]] = TypeUtilities.TypeDict()
json_decoders:dict[str,type[CustomJson.Coder]] = {}

def hash_data(data:Any) -> int:
    '''
    Tries its best to hash anything, including mutable objects. Will throw an exception if it can't figure out how.
    :data: The data to hash
    '''
    return hash_type_table[type(data)](data)

def register_decorator[T](
    name:str|None,
    hashing_method:Callable[[Any],int]|None=None,
    *,
    requires_subcomponent:bool=False,
    sortable:str|list[str]|None=None,
    is_file:bool=False,
    is_iterable:bool=False,
    is_mapping:bool=False,
    is_string:bool=False,
    can_contain:set[type]|None=None,
    json_coder:type[CustomJson.Coder]|NoCoder|None=None,
) -> Callable[[type[T]],type[T]]:
    def decorator(_type:type[T]) -> type[T]:
        register_type(
            _type,
            name,
            hashing_method=hashing_method,
            requires_subcomponent=requires_subcomponent,
            sortable=sortable,
            is_file=is_file,
            is_iterable=is_iterable,
            is_mapping=is_mapping,
            is_string=is_string,
            can_contain=can_contain,
            json_coder=json_coder,
        )
        return _type
    return decorator

def register_type[T](
    _type:type[T],
    name:str|None,
    hashing_method:Callable[[T],int]|None=None,
    *,
    requires_subcomponent:bool|None=None,
    sortable:str|list[str]|None=None,
    is_file:bool=False,
    is_iterable:bool=False,
    is_mapping:bool=False,
    is_string:bool=False,
    can_contain:set[type]|None=None,
    json_coder:type[CustomJson.Coder]|NoCoder|None=None,
) -> None:
    '''
    Makes a type referrable to via Components. If a type subclasses a type
    already added using this method (including default types), it does not need
    to specify everything again; these properties are inherited.

    :_type: The class to be added.
    :name: The string Components should use to refer to this type. If None, cannot be referred to by Components.
    :hashing_method: The method Structures use to hash the data (even if it is not a primitive).
    :requires_subcomponent: If True, Components that use this type must have a subcomponent.
    :sortable: The category/ies of types this type is sortable with.
    :is_file: If this type is File-like.
    :is_iterable: If this type follows the Iterable protocol.
    :is_mapping: If this type follows the Mapping protocol.
    :is_string: If this type acts like a str.
    :can_contain: If present, Components will only let this type contain these types.
    :json_coder: Coder used to convert the type to JSON and vice versa.
    '''
    if name is not None:
        default_types[name] = _type
    if hashing_method is not None:
        hash_type_table[_type] = hashing_method
    if requires_subcomponent is not None:
        # This property only inherits if requires_subcomponent is None
        if requires_subcomponent is True:
            requires_subcomponent_types.add(_type)
        else:
            requires_subcomponent_types.add_not(_type)
    if sortable is not None:
        sortable = [sortable] if not isinstance(sortable, list) else sortable
        sortable_types.add(_type)
        for category in sortable:
            mutually_sortable[category].add(_type)
    if is_file:
        file_types.add(_type)
    if is_iterable:
        iterable_types.add(_type)
    if is_mapping:
        mapping_types.add(_type)
    if is_string:
        string_types.add(_type)
    if can_contain is not None:
        containment_types[_type] = TypeUtilities.TypeSet(can_contain)
    if isinstance(json_coder, NoCoder):
        json_encoders.add_not(_type)
    elif json_coder is not None:
        json_encoders[_type] = json_coder
        json_decoders[json_coder.special_type_name] = json_coder

register_type(bool, "bool", hash, sortable="default")
register_type(bytearray, None, lambda data: hash(tuple(item for item in data)), is_iterable=True)
register_type(bytes, None, hash, is_iterable=True, is_string=True)
register_type(complex, None, hash)
register_type(dict, "dict", lambda data: hash(tuple((hash(key), hash_data(value)) for key, value in data.items())), requires_subcomponent=True, is_mapping=True)
register_type(float, "float", hash, sortable="default")
register_type(frozenset, None, hash, is_iterable=True)
register_type(int, "int", hash, sortable="default")
register_type(list, "list", lambda data: hash(tuple(hash_data(item) for item in data)), requires_subcomponent=True, is_iterable=True)
register_type(memoryview, None, hash)
register_type(type(None), "null", hash, sortable="null")
register_type(range, None, hash)
register_type(set, None, lambda data: hash(tuple(item for item in data)), is_iterable=True)
register_type(str, "str", hash, sortable="string", is_string=True)
register_type(tuple, "tuple", lambda data: hash(tuple(hash_data(item) for item in data)), is_iterable=True)
