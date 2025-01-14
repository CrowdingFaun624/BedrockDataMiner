from collections import defaultdict
from types import EllipsisType
from typing import Any, Callable

import Domain.Domain as Domain
import Domain.Domains as Domains
import Utilities.CustomJson as CustomJson
import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts
import Utilities.TypeUtilities as TypeUtilities


class NoCoder():
    '''
    Used to annotate that a type specifically has no JSON Coder.
    '''
    # does nothing otherwise.
    ...

no_coder = NoCoder()

class TypeStuff():
    '''
    Class that keeps track of typing. There is one primary one for all Domains
    and an additional one for each domain.
    '''

    __slots__ = (
        "containment_types",
        "default_types",
        "domain",
        "file_types",
        "hash_type_table",
        "iterable_types",
        "json_decoders",
        "json_encoders",
        "linked_type_stuffs",
        "mapping_types",
        "mutually_sortable",
        "requires_subcomponent_types",
        "sortable_types",
        "string_types",
    )

    def __init__(
        self,
        domain:"Domain.Domain|None",
        linked_type_stuffs:list["TypeStuff"]|None=None,
        default_types:dict[str,type]|None=None,
        requires_subcomponent_types:TypeUtilities.TypeSet|None=None,
        sortable_types:TypeUtilities.TypeSet|None=None,
        mutually_sortable:defaultdict[str,TypeUtilities.TypeSet]|None=None,
        file_types:TypeUtilities.TypeSet|None=None,
        iterable_types:TypeUtilities.TypeSet|None=None,
        mapping_types:TypeUtilities.TypeSet|None=None,
        string_types:TypeUtilities.TypeSet|None=None,
        containment_types:TypeUtilities.TypeDict[object, TypeUtilities.TypeSet]|None=None,
        hash_type_table:TypeUtilities.TypeDict[Any,Callable[[Any, "TypeStuff"],int]]|None=None,
        json_encoders:TypeUtilities.TypeDict[object, type[CustomJson.Coder]]|None=None,
        json_decoders:dict[str,type[CustomJson.Coder]]|None=None,
    ) -> None:
        self.domain = domain
        self.linked_type_stuffs = [] if linked_type_stuffs is None else linked_type_stuffs
        self.default_types:dict[str,type] = {} if default_types is None else default_types
        self.requires_subcomponent_types = TypeUtilities.TypeSet() if requires_subcomponent_types is None else requires_subcomponent_types
        self.sortable_types = TypeUtilities.TypeSet() if sortable_types is None else sortable_types
        self.mutually_sortable:defaultdict[str,TypeUtilities.TypeSet] = defaultdict(lambda: TypeUtilities.TypeSet()) if mutually_sortable is None else mutually_sortable
        self.file_types = TypeUtilities.TypeSet() if file_types is None else file_types
        self.iterable_types = TypeUtilities.TypeSet() if iterable_types is None else iterable_types
        self.mapping_types = TypeUtilities.TypeSet() if mapping_types is None else mapping_types
        self.string_types = TypeUtilities.TypeSet() if string_types is None else string_types
        self.containment_types:TypeUtilities.TypeDict[object, TypeUtilities.TypeSet] = TypeUtilities.TypeDict() if containment_types is None else containment_types
        self.hash_type_table:TypeUtilities.TypeDict[Any,Callable[[Any, TypeStuff],int]] = TypeUtilities.TypeDict() if hash_type_table is None else hash_type_table
        self.json_encoders:TypeUtilities.TypeDict[object, type[CustomJson.Coder]] = TypeUtilities.TypeDict() if json_encoders is None else json_encoders
        self.json_decoders:dict[str,type[CustomJson.Coder]] = {} if json_decoders is None else json_decoders

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.domain.name if self.domain is not None else "primary"}>"

    def __hash__(self) -> int:
        return hash(self.domain)

    def copy(self) -> "TypeStuff":
        return TypeStuff(
            domain=self.domain,
            linked_type_stuffs=self.linked_type_stuffs.copy(),
            default_types=self.default_types.copy(),
            requires_subcomponent_types=self.requires_subcomponent_types.copy(),
            sortable_types=self.sortable_types.copy(),
            mutually_sortable=self.mutually_sortable.copy(),
            file_types=self.file_types.copy(),
            iterable_types=self.iterable_types.copy(),
            mapping_types=self.mapping_types.copy(),
            string_types=self.string_types.copy(),
            containment_types=self.containment_types.copy(),
            hash_type_table=self.hash_type_table.copy(),
            json_encoders=self.json_encoders.copy(),
            json_decoders=self.json_decoders.copy(),
        )

    def extend(self, other:"TypeStuff") -> None:
        self.default_types.update(other.default_types)
        self.requires_subcomponent_types.update(other.requires_subcomponent_types)
        self.sortable_types.update(other.sortable_types)
        for category, sortable_types in other.mutually_sortable.items():
            self.mutually_sortable[category].update(sortable_types)
        self.file_types.update(other.file_types)
        self.iterable_types.update(other.iterable_types)
        self.mapping_types.update(other.mapping_types)
        self.string_types.update(other.string_types)
        self.containment_types.update(other.containment_types)
        self.hash_type_table.update(other.hash_type_table)
        self.json_encoders.update(other.json_encoders)
        self.json_decoders.update(other.json_decoders)

    def link(self, other:"TypeStuff") -> None:
        '''
        When adding to self, also add to `other`.
        '''
        other.linked_type_stuffs.append(self)

    def get_cascading_dependencies(self, memo:set["TypeStuff"]) -> list["TypeStuff"]:
        if self not in memo:
            output:list[TypeStuff] = []
            memo.add(self)
            for child in self.linked_type_stuffs:
                output.extend(child.get_cascading_dependencies(memo))
            output.append(self)
            return output
        else:
            return []

    def hash_data(self, data:Any) -> int:
        '''
        Tries its best to hash anything, including mutable objects.
        :data: The data to hash
        '''
        return self.hash_type_table[type(data)](data, self)

primary_type_stuff = TypeStuff(None)
'''
TypeStuff for non-Script types.
'''

def register_decorator[T](
    name:str|None,
    hashing_method:Callable[[Any, TypeStuff],int]|None|EllipsisType,
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
    '''
    Makes a type referrable to via Components. If a type subclasses a type
    already added using this method (including default types), it does not need
    to specify everything again; these properties are inherited.

    :name: The string Components should use to refer to this type. If None, cannot be referred to by Components.
    :hashing_method: The method Structures use to hash the data (even if it is not a primitive).\
        Use None to inherit from a subclass's hash method and ... to use the `hash` function.
    :requires_subcomponent: If True, Components that use this type must have a subcomponent.
    :sortable: The category/ies of types this type is sortable with.
    :is_file: If this type is File-like.
    :is_iterable: If this type follows the Iterable protocol.
    :is_mapping: If this type follows the Mapping protocol.
    :is_string: If this type acts like a str.
    :can_contain: If present, Components will only let this type contain these types.
    :json_coder: Coder used to convert the type to JSON and vice versa.
    '''
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
    hashing_method:Callable[[T, TypeStuff],int]|None|EllipsisType,
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
    :hashing_method: The method Structures use to hash the data (even if it is not a primitive).\
        Use None to inherit from a subclass's hash method and ... to use the `hash` function.
    :requires_subcomponent: If True, Components that use this type must have a subcomponent.
    :sortable: The category/ies of types this type is sortable with.
    :is_file: If this type is File-like.
    :is_iterable: If this type follows the Iterable protocol.
    :is_mapping: If this type follows the Mapping protocol.
    :is_string: If this type acts like a str.
    :can_contain: If present, Components will only let this type contain these types.
    :json_coder: Coder used to convert the type to JSON and vice versa.
    '''
    domain_name = Domains.get_domain_name_from_module(_type.__module__)
    if domain_name is None and Scripts.has_imported_scripts.has_imported_scripts:
        raise Exceptions.ImportOrderError(_type.__module__)
    type_stuff = primary_type_stuff if domain_name is None else Domains.domains[domain_name].type_stuff
    type_stuffs = type_stuff.get_cascading_dependencies(set())
    for type_stuff in type_stuffs:
        if name is not None:
            type_stuff.default_types[name] = _type
        if hashing_method is not None:
            type_stuff.hash_type_table[_type] = (lambda data, type_stuff: hash(data)) if hashing_method is ... else hashing_method
        if requires_subcomponent is not None:
            # This property only inherits if requires_subcomponent is None
            if requires_subcomponent is True:
                type_stuff.requires_subcomponent_types.add(_type)
            else:
                type_stuff.requires_subcomponent_types.add_not(_type)
        if sortable is not None:
            sortable = [sortable] if not isinstance(sortable, list) else sortable
            type_stuff.sortable_types.add(_type)
            for category in sortable:
                type_stuff.mutually_sortable[category].add(_type)
        if is_file:
            type_stuff.file_types.add(_type)
        if is_iterable:
            type_stuff.iterable_types.add(_type)
        if is_mapping:
            type_stuff.mapping_types.add(_type)
        if is_string:
            type_stuff.string_types.add(_type)
        if can_contain is not None:
            type_stuff.containment_types[_type] = TypeUtilities.TypeSet(can_contain)
        if isinstance(json_coder, NoCoder):
            type_stuff.json_encoders.add_not(_type)
        elif json_coder is not None:
            type_stuff.json_encoders[_type] = json_coder
            type_stuff.json_decoders[json_coder.special_type_name] = json_coder

register_type(bool, "bool", ..., sortable="default")
register_type(bytearray, None, lambda data, type_stuff: hash(tuple(item for item in data)), is_iterable=True)
register_type(bytes, None, ..., is_iterable=True, is_string=True)
register_type(complex, None, ...)
register_type(dict, "dict", lambda data, type_stuff: hash(tuple((hash(key), type_stuff.hash_data(value)) for key, value in data.items())), requires_subcomponent=True, is_mapping=True)
register_type(float, "float", ..., sortable="default")
register_type(frozenset, None, ..., is_iterable=True)
register_type(int, "int", ..., sortable="default")
register_type(list, "list", lambda data, type_stuff: hash(tuple(type_stuff.hash_data(item) for item in data)), requires_subcomponent=True, is_iterable=True)
register_type(memoryview, None, ...)
register_type(type(None), "null", ..., sortable="null")
register_type(range, None, ...)
register_type(set, None, lambda data, type_stuff: hash(tuple(item for item in data)), is_iterable=True)
register_type(str, "str", ..., sortable="string", is_string=True)
register_type(tuple, "tuple", lambda data, type_stuff: hash(tuple(type_stuff.hash_data(item) for item in data)), is_iterable=True)
