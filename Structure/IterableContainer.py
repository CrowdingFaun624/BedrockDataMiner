from typing import Hashable, Iterable, Mapping, cast

import Structure.Container as Con


def icon_from_list[K, V, D](items:Iterable[tuple[K, V]], data:D) -> "ICon[K, V, D]":
    '''
    Creates a new IterableContainer from a list of tuples of Containers.
    '''
    items_dict:dict[K, V] = {}
    hashable_stuff:list[Hashable] = []
    for key, value in items:
        items_dict[key] = value
        hashable_stuff.append(key)
        hashable_stuff.append(value)
    items_hash = hash(tuple(hashable_stuff))
    return ICon(data, items_dict, items_hash)

def idon_from_list[K, V, D, KC, VC](items:Iterable[tuple[K, V]], containers:Mapping[int,"ICon[KC, VC, D]"]) -> "IDon[K, V, D, KC, VC]":
    '''
    Creates a new IterableDiffContainer from a list of tuples of Containers.
    '''
    items_dict:dict[K, V] = {}
    hashable_stuff:list[Hashable] = []
    for key, value in items:
        items_dict[key] = value
        hashable_stuff.append(key)
        hashable_stuff.append(value)
    items_hash = hash(tuple(hashable_stuff))
    return IDon(containers, items_dict, items_hash)

class ICon[K:Hashable, V, D](Con.Con[D]):

    __slots__ = (
        "_items",
        "data",
        "hash",
    )

    def __init__(self, data:D, items:dict[K, V], hash:int) -> None:
        self.data = data
        self._items = items
        self.hash = hash

    def items(self) -> Iterable[tuple[K, V]]:
        return self._items.items()

    def keys(self) -> Iterable[K]:
        return self._items.keys()

    def values(self) -> Iterable[V]:
        return self._items.values()

    def as_don(self, bundle:tuple[int,...]) -> "IDon[K, V, D, K, V]":
        return IDon({branch: self for branch in bundle}, self._items, self.hash)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._items}>"

class IDon[K:Hashable, V, D, KC:Hashable, VC](Con.Don[D]):

    __slots__ = (
        "_containers",
        "_items",
        "hash",
    )

    def __init__(self, containers:Mapping[int,ICon[KC, VC, D]], items:dict[K, V], hash:int) -> None:
        self._containers:Mapping[int,ICon[KC, VC, D]] = containers
        self._items = items
        self.hash = hash

    def get_con(self, branch:int) -> "ICon[KC, VC, D]":
        return self._containers[branch]

    @property
    def last_container(self) -> ICon[KC, VC, D]:
        return self._containers[cast(int, next(iter(reversed(self._containers))))]

    def items(self) -> Iterable[tuple[K, V]]:
        return self._items.items()

    def keys(self) -> Iterable[K]:
        return self._items.keys()

    def values(self) -> Iterable[V]:
        return self._items.values()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._items}>"
