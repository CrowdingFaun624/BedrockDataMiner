from typing import TYPE_CHECKING, Sequence

from Component.ComponentObject import ComponentObject
from Structure.StructureInfo import StructureInfo

if TYPE_CHECKING:
    from _typeshed import (
        SupportsDunderGE,
        SupportsDunderGT,
        SupportsDunderLE,
        SupportsDunderLT,
    )

class Filter(ComponentObject):
    '''Object for changing flow based on StructureInfo content.'''

    __slots__ = ()

    def link_filter(self) -> None:
        pass

    def filter(self, structure_info:StructureInfo) -> bool:
        ...

class ValueFilter[A](Filter):

    __slots__ = (
        "default",
        "key",
        "value",
    )

    def link_value_filter(self, key:str, value:A, default:bool) -> None:
        self.key = key
        self.value = value
        self.default = default

    def filter(self, structure_info:StructureInfo) -> bool:
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

    def link_meta_filter(self, subfilters:Sequence[Filter]) -> None:
        self.subfilters = subfilters

class KeyFilter(Filter):

    __slots__ = (
        "key",
    )

    def link_key_filter(self, key:str) -> None:
        self.key = key

class KeyPresentFilter(KeyFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo) -> bool:
        return self.key in structure_info

class KeyNotPresentFilter(KeyFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo) -> bool:
        return self.key not in structure_info

class AndFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo) -> bool:
        return all(subfilter.filter(structure_info) for subfilter in self.subfilters)

class OrFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo) -> bool:
        return any(subfilter.filter(structure_info) for subfilter in self.subfilters)

class NandFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo) -> bool:
        return not all(subfilter.filter(structure_info) for subfilter in self.subfilters)

class NorFilter(MetaFilter):

    __slots__ = ()

    def filter(self, structure_info: StructureInfo) -> bool:
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
