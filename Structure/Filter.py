from typing import TYPE_CHECKING

import Structure.StructureInfo as StructureInfo

if TYPE_CHECKING:
    from _typeshed import (
        SupportsDunderGE,
        SupportsDunderGT,
        SupportsDunderLE,
        SupportsDunderLT,
    )

class Filter():
    '''Object for changing flow based on StructureInfo content.'''

    __slots__ = (
        "name",
    )

    def __init__(self, name:str) -> None:
        self.name = name

    def link_subcomponents(self) -> None:
        pass

    def filter(self, structure_info:StructureInfo.StructureInfo) -> bool:
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

class ValueFilter[A](Filter):

    __slots__ = (
        "default",
        "key",
        "value",
    )

    def __init__(self, name:str, key: str, value:A, default:bool) -> None:
        super().__init__(name)
        self.key = key
        self.value = value
        self.default = default

    def filter(self, structure_info:StructureInfo.StructureInfo) -> bool:
        value = structure_info.get(self.key, ...)
        if value is ...:
            return self.default
        return self._filter(value)

    def _filter(self, value:A) -> bool:
        ...

class MetaFilter(Filter):

    __slots__ = (
        "subfilters",
    )

    def link_subcomponents(self, subfilters:list[Filter]) -> None:
        super().link_subcomponents()
        self.subfilters = subfilters

class KeyFilter(Filter):

    __slots__ = (
        "key",
    )

    def __init__(self, name: str, key:str) -> None:
        super().__init__(name)
        self.key = key


class KeyPresentFilter(KeyFilter):

    def filter(self, structure_info: StructureInfo.StructureInfo) -> bool:
        return self.key in structure_info

class KeyNotPresentFilter(KeyFilter):

    def filter(self, structure_info: StructureInfo.StructureInfo) -> bool:
        return self.key not in structure_info

class AndFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo.StructureInfo) -> bool:
        return all(subfilter.filter(structure_info) for subfilter in self.subfilters)

class OrFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo.StructureInfo) -> bool:
        return any(subfilter.filter(structure_info) for subfilter in self.subfilters)

class NandFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo.StructureInfo) -> bool:
        return not all(subfilter.filter(structure_info) for subfilter in self.subfilters)

class NorFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo.StructureInfo) -> bool:
        return not any(subfilter.filter(structure_info) for subfilter in self.subfilters)

class EqFilter[A](ValueFilter[A]):

    __slots__ = ()

    def _filter(self, value: A) -> bool:
        return value == self.value

class NeFilter[A](ValueFilter[A]):

    __slots__ = ()

    def _filter(self, value: A) -> bool:
        return value != self.value

class GtFilter[A: "SupportsDunderGT"](ValueFilter[A]):

    __slots__ = ()

    def _filter(self, value: A) -> bool:
        return value > self.value

class LtFilter[A: "SupportsDunderLT"](ValueFilter[A]):

    __slots__ = ()

    def _filter(self, value: A) -> bool:
        return value < self.value

class GeFilter[A: "SupportsDunderGE"](ValueFilter[A]):

    __slots__ = ()

    def _filter(self, value: A) -> bool:
        return value >= self.value

class LeFilter[A: "SupportsDunderLE"](ValueFilter[A]):

    __slots__ = ()

    def _filter(self, value: A) -> bool:
        return value <= self.value
