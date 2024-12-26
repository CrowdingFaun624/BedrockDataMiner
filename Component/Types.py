from collections import defaultdict
from typing import Any, Callable, Generic, Iterable, Iterator, Mapping, TypeVar

import Utilities.CustomJson as CustomJson

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")

class NoCoder():
    '''
    Used to annotate that a type specifically has no JSON Coder.
    '''
    # does nothing otherwise.
    ...

no_coder = NoCoder()

class TypeSet(Generic[T]):

    def __init__(self, types:Iterable[type[T]]|None=None) -> None:
        self.types:set[type[T]] = set(types) if types is not None else set()
        self.not_types:set[type] = set()

    def __iter__(self) -> Iterator[type[T]]:
        return iter(self.types)

    def __repr__(self) -> str:
        return "<%s {%s}>" % (self.__class__.__name__, ", ".join(contained_type.__name__ for contained_type in self.types))

    def __contains__(self, _type:type[T]) -> bool:
        if _type in self.types: return True
        elif _type in self.not_types: return False
        else:
            for other_type in self.types:
                if issubclass(_type, other_type):
                    self.types.add(_type)
                    return True
            else:
                self.not_types.add(_type)
                return False

    def add(self, _type:type[T]) -> None:
        self.types.add(_type)
        self.not_types.discard(_type)

    def add_not(self, _type:type[T]) -> None:
        self.not_types.add(_type)
        self.types.discard(_type)

class TypeDict(Generic[T, A]):

    def __init__(self, types:Mapping[type[T], A]|None=None) -> None:
        self.types:dict[type[T],A] = dict(types) if types is not None else {}
        self.not_types:set[type] = set()

    def __repr__(self) -> str:
        return "<%s {%s}>" % (self.__class__.__name__, ", ".join("%s: %s" % (contained_type.__name__, value) for contained_type, value in self.types.items()))

    def __contains__(self, _type:type[T]) -> bool:
        if _type in self.types: return True
        elif _type in self.not_types: return False
        else:
            for other_type, value in self.types.items():
                if issubclass(_type, other_type):
                    self.types[_type] = value
                    return True
            else:
                self.not_types.add(_type)
                return False

    def __setitem__(self, _type:type[T], value:A) -> None:
        self.types[_type] = value
        self.not_types.discard(_type)

    def add_not(self, _type:type[T]) -> None:
        self.types.pop(_type, None)
        self.not_types.add(_type)

    def __getitem__(self, _type:type[T]) -> A:
        if (output := self.types.get(_type, ...)) is not ...:
            return output
        elif _type in self.not_types:
            raise KeyError(_type)
        else:
            for other_type, value in self.types.items():
                if issubclass(_type, other_type):
                    self.types[_type] = value
                    return value
            else:
                self.not_types.add(_type)
                raise KeyError(_type)

    def get(self, _type:type[T], default:B=None) -> A|B:
        if (output := self.types.get(_type, ...)) is not ...:
            return output
        elif _type in self.not_types:
            return default
        else:
            for other_type, value in self.types.items():
                if issubclass(_type, other_type):
                    self.types[_type] = value
                    return value
            else:
                self.not_types.add(_type)
                return default

default_types:dict[str,type] = {}
requires_subcomponent_types = TypeSet()
sortable_types = TypeSet()
mutually_sortable:defaultdict[str,TypeSet] = defaultdict(lambda: TypeSet())
file_types = TypeSet()
iterable_types = TypeSet()
mapping_types = TypeSet()
string_types = TypeSet()
containment_types:TypeDict[object, TypeSet] = TypeDict()
hash_type_table:TypeDict[Any,Callable[[Any],int]] = TypeDict()
json_encoders:TypeDict[object, type[CustomJson.Coder]] = TypeDict()
json_decoders:dict[str,type[CustomJson.Coder]] = {}

def hash_data(data:Any) -> int:
    '''
    Tries its best to hash anything, including mutable objects. Will throw an exception if it can't figure out how.
    :data: The data to hash
    '''
    return hash_type_table[type(data)](data)

def register_decorator(
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

def register_type(
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
        containment_types[_type] = TypeSet(can_contain)
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
