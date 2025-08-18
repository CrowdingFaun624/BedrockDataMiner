from collections import defaultdict
from types import EllipsisType
from typing import Any, Callable, Iterable

import Domain.Domain as Domain
from Domain.Domains import domains, get_domain_name_from_module
from Utilities.CustomJson import Coder
from Utilities.TypeUtilities import TypeDict, TypeSet


class NoCoder():
    """
    Used to annotate that a type specifically has no JSON Coder.
    """

    __slots__ = ()

    # does nothing otherwise.
    ...

no_coder = NoCoder()

class TypeStuff():
    """
    Class that keeps track of typing. There is one primary one for all Domains
    and an additional one for each domain.
    """

    __slots__ = (
        "iterate_table",
        "containment_types",
        "default_types",
        "domain",
        "file_types",
        "hash_type_table",
        "json_decoders",
        "json_encoders",
        "linked_type_stuffs",
        "mutually_sortable",
        "requires_subcomponent_types",
        "sortable_types",
        "string_types",
        "type_names",
    )

    def __init__(
        self,
        domain:"Domain.Domain|None",
        linked_type_stuffs:list["TypeStuff"]|None=None,
        default_types:dict[str,type]|None=None,
        requires_subcomponent_types:TypeSet|None=None,
        sortable_types:TypeSet|None=None,
        mutually_sortable:defaultdict[str,TypeSet]|None=None,
        file_types:TypeSet|None=None,
        string_types:TypeSet|None=None,
        containment_types:TypeDict[object, TypeSet]|None=None,
        hash_type_table:TypeDict[Any,Callable[[Any, "TypeStuff"],int]]|None=None,
        iterate_table:TypeDict[Any, Callable[[Any], Iterable[tuple[Any, Any]]]]|None=None,
        json_encoders:TypeDict[object, type[Coder]]|None=None,
        json_decoders:dict[str,type[Coder]]|None=None,
    ) -> None:
        self.domain = domain
        self.linked_type_stuffs = [] if linked_type_stuffs is None else linked_type_stuffs
        self.default_types:dict[str,type] = {} if default_types is None else default_types
        self.type_names:dict[type, str] = {} if default_types is None else {value: key for key, value in default_types.items()}
        self.requires_subcomponent_types = TypeSet() if requires_subcomponent_types is None else requires_subcomponent_types
        self.sortable_types = TypeSet() if sortable_types is None else sortable_types
        self.mutually_sortable:defaultdict[str,TypeSet] = defaultdict(lambda: TypeSet()) if mutually_sortable is None else mutually_sortable
        self.file_types = TypeSet() if file_types is None else file_types
        self.string_types = TypeSet() if string_types is None else string_types
        self.containment_types:TypeDict[object, TypeSet] = TypeDict() if containment_types is None else containment_types
        self.hash_type_table:TypeDict[Any,Callable[[Any, TypeStuff],int]] = TypeDict() if hash_type_table is None else hash_type_table
        self.iterate_table:TypeDict[Any,Callable[[Any], Iterable[tuple[Any, Any]]]] = TypeDict() if iterate_table is None else iterate_table
        self.json_encoders:TypeDict[object, type[Coder]] = TypeDict() if json_encoders is None else json_encoders
        self.json_decoders:dict[str,type[Coder]] = {} if json_decoders is None else json_decoders

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.domain.name if self.domain is not None else "primary"}>"

    def __hash__(self) -> int:
        return hash(self.domain)

    def copy(self) -> "TypeStuff":
        return TypeStuff(
            domain=self.domain,
            linked_type_stuffs=self.linked_type_stuffs.copy(),
            default_types=self.default_types.copy(),
            # type_names needs no copying, since it will be copied from default_types.
            requires_subcomponent_types=self.requires_subcomponent_types.copy(),
            sortable_types=self.sortable_types.copy(),
            mutually_sortable=self.mutually_sortable.copy(),
            file_types=self.file_types.copy(),
            string_types=self.string_types.copy(),
            containment_types=self.containment_types.copy(),
            hash_type_table=self.hash_type_table.copy(),
            iterate_table=self.iterate_table.copy(),
            json_encoders=self.json_encoders.copy(),
            json_decoders=self.json_decoders.copy(),
        )

    def extend(self, other:"TypeStuff") -> None:
        self.default_types.update(other.default_types)
        self.type_names.update(other.type_names)
        self.requires_subcomponent_types.update(other.requires_subcomponent_types)
        self.sortable_types.update(other.sortable_types)
        for category, sortable_types in other.mutually_sortable.items():
            self.mutually_sortable[category].update(sortable_types)
        self.file_types.update(other.file_types)
        self.string_types.update(other.string_types)
        self.containment_types.update(other.containment_types)
        self.hash_type_table.update(other.hash_type_table)
        self.iterate_table.update(other.iterate_table)
        self.json_encoders.update(other.json_encoders)
        self.json_decoders.update(other.json_decoders)

    def link(self, other:"TypeStuff") -> None:
        """
        When adding to self, also add to `other`.
        """
        other.linked_type_stuffs.append(self)

    def get_cascading_dependencies(self, memo:set["TypeStuff"]) -> Iterable["TypeStuff"]:
        if self not in memo:
            output:list[TypeStuff] = []
            memo.add(self)
            for child in self.linked_type_stuffs:
                output.extend(child.get_cascading_dependencies(memo))
            output.append(self)
            return output
        else:
            return ()

    def hash_data(self, data:Any) -> int:
        """
        Tries its best to hash anything, including mutable objects.

        :param data: The data to hash
        """
        return self.hash_type_table[type(data)](data, self)

    def iterate_data(self, data:Any) -> Iterable[tuple[Any, Any]]:
        return self.iterate_table[type(data)](data)

primary_type_stuff = TypeStuff(None)
"""
TypeStuff for non-Script types.
"""

def register_decorator[T](
    name:str|None,
    hashing_method:Callable[[T, TypeStuff],int]|None|EllipsisType,
    *,
    iterate_method:Callable[[T], Iterable[tuple[Any, Any]]]|None=None,
    requires_subcomponent:bool=False,
    sortable:str|list[str]|None=None,
    is_file:bool=False,
    is_string:bool=False,
    can_contain:set[type]|None=None,
    json_coder:type[Coder]|NoCoder|None=None,
) -> Callable[[type[T]],type[T]]:
    """
    Makes a type referrable to via Components. If a type subclasses a type
    already added using this method (including default types), it does not need
    to specify everything again; these properties are inherited.

    :param name: The string Components should use to refer to this type. If None, cannot be referred to by Components.
    :param hashing_method: The method Structures use to hash the data (even if it is not a primitive).\
        Use None to inherit from a subclass's hash method and ... to use the `hash` function.
    :param iterate_method: The method Structures use to iterate the data.\
        Use None to inherit from a subclass's iterate method and ... to wrap it in a SimpleContainer.
    :param requires_subcomponent: If True, Components that use this type must have a subcomponent.
    :param sortable: The category/ies of types this type is sortable with.
    :param is_file: If this type is File-like.
    :param is_string: If this type acts like a str.
    :param can_contain: If present, Components will only let this type contain these types.
    :param json_coder: Coder used to convert the type to JSON and vice versa.
    """
    def decorator(_type:type[T]) -> type[T]:
        register_type(
            _type,
            name,
            hashing_method=hashing_method,
            iterate_method=iterate_method,
            requires_subcomponent=requires_subcomponent,
            sortable=sortable,
            is_file=is_file,
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
    iterate_method:Callable[[T], Iterable[tuple[Any, Any]]]|None=None,
    requires_subcomponent:bool|None=None,
    sortable:str|list[str]|None=None,
    is_file:bool=False,
    is_string:bool=False,
    can_contain:set[type]|None=None,
    json_coder:type[Coder]|NoCoder|None=None,
) -> None:
    """
    Makes a type referrable to via Components. If a type subclasses a type
    already added using this method (including default types), it does not need
    to specify everything again; these properties are inherited.

    :param _type: The class to be added.
    :param name: The string Components should use to refer to this type. If None, cannot be referred to by Components.
    :param hashing_method: The method Structures use to hash the data (even if it is not a primitive).\
        Use None to inherit from a subclass's hash method and ... to use the `hash` function.
    :param iterate_method: The method Structures use to iterate over the data.\
        Use None to inherit from a subclass's iterate method.
    :param requires_subcomponent: If True, Components that use this type must have a subcomponent.
    :param sortable: The category/ies of types this type is sortable with.
    :param is_file: If this type is File-like.
    :param is_string: If this type acts like a str.
    :param can_contain: If present, Components will only let this type contain these types.
    :param json_coder: Coder used to convert the type to JSON and vice versa.
    """
    domain_name = get_domain_name_from_module(_type.__module__)
    type_stuff = primary_type_stuff if domain_name is None else domains[domain_name].type_stuff
    type_stuffs = type_stuff.get_cascading_dependencies(set())
    for type_stuff in type_stuffs:
        if name is not None:
            type_stuff.default_types[name] = _type
        if hashing_method is not None:
            type_stuff.hash_type_table[_type] = (lambda data, type_stuff: hash(data)) if hashing_method is ... else hashing_method
        if iterate_method is not None:
            type_stuff.iterate_table[_type] = iterate_method
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
        if is_string:
            type_stuff.string_types.add(_type)
        if can_contain is not None:
            type_stuff.containment_types[_type] = TypeSet(can_contain)
        if isinstance(json_coder, NoCoder):
            type_stuff.json_encoders.add_not(_type)
        elif json_coder is not None:
            type_stuff.json_encoders[_type] = json_coder
            type_stuff.json_decoders[json_coder.special_type_name] = json_coder

register_type(bool, "bool", ..., sortable="default")
register_type(bytearray, None, lambda data, type_stuff: hash(tuple(item for item in data)), iterate_method=enumerate)
register_type(bytes, None, ..., is_string=True)
register_type(complex, None, ...)
register_type(dict, "dict", lambda data, type_stuff: hash(tuple((hash(key), type_stuff.hash_data(value)) for key, value in data.items())), iterate_method=lambda data: data.items(), requires_subcomponent=True)
register_type(float, "float", ..., sortable="default")
register_type(frozenset, None, ..., iterate_method=enumerate)
register_type(int, "int", ..., sortable="default")
register_type(list, "list", lambda data, type_stuff: hash(tuple(type_stuff.hash_data(item) for item in data)), iterate_method=enumerate, requires_subcomponent=True)
register_type(memoryview, None, ...)
register_type(type(None), "null", ..., sortable="null")
register_type(range, None, ...)
register_type(set, None, lambda data, type_stuff: hash(tuple(item for item in data)), iterate_method=enumerate)
register_type(str, "str", ..., sortable="string", is_string=True)
register_type(tuple, "tuple", lambda data, type_stuff: hash(tuple(type_stuff.hash_data(item) for item in data)), iterate_method=enumerate)
