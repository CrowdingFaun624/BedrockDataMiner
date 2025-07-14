from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Structure.Filter as Filter
from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

FILTER_PATTERN:Pattern["FilterComponent"] = Pattern("is_filter")

class FilterComponent[A: Filter.Filter](Component[A]):

    my_capabilities = Capabilities(is_filter=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("type", False, str),
    )
    filter_class:type[A]

    __slots__ = ()

class ValueFilterComponent[A: Filter.ValueFilter](FilterComponent[A]):

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("default", False, bool),
        TypedDictKeyTypeVerifier("key", True, str),
        TypedDictKeyTypeVerifier("value", True, object),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "default",
        "key",
        "value",
    )

    def initialize_fields(self, data: ComponentTyping.ValueFilterTypedDict) -> Sequence[Field]:
        self.default = data.get("default", False)
        self.key = data["key"]
        self.value = data["value"]
        return ()

    def create_final(self, trace:Trace) -> Filter.ValueFilter:
        return self.filter_class(
            name=self.name,
            key=self.key,
            value=self.value,
            default=self.default,
        )

class KeyFilterComponent[A: Filter.KeyFilter](FilterComponent[A]):

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("key", True, str),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "key",
    )

    def initialize_fields(self, data: ComponentTyping.KeyFilterTypedDict) -> Sequence[Field]:
        self.key = data["key"]
        return ()

    def create_final(self, trace:Trace) -> A:
        return self.filter_class(
            name=self.name,
            key=self.key,
        )

class MetaFilterComponent[A: Filter.MetaFilter](FilterComponent[A]):

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("subfilters", True, ListTypeVerifier((dict, str), list)),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "subfilters_field",
    )

    def initialize_fields(self, data: ComponentTyping.MetaFilterTypedDict) -> Sequence[Field]:
        self.subfilters_field = ComponentListField(data["subfilters"], FILTER_PATTERN, ("subfilters",))
        return (self.subfilters_field,)

    def create_final(self, trace:Trace) -> A:
        return self.filter_class(
            name=self.name,
        )

    def link_finals(self, trace:Trace) -> None:
        super().link_finals(trace)
        self.final.link_subcomponents(
            subfilters=list(self.subfilters_field.map(lambda subcomponent: subcomponent.final)),
        )

class KeyPresentFilterComponent(KeyFilterComponent[Filter.KeyPresentFilter]):

    class_name = "KeyPresentFilter"
    filter_class = Filter.KeyPresentFilter
    __slots__ = ()

class KeyNotPresentFilterComponent(KeyFilterComponent[Filter.KeyNotPresentFilter]):

    class_name = "KeyNotPresentFilter"
    filter_class = Filter.KeyNotPresentFilter
    __slots__ = ()

class AndFilterComponent(MetaFilterComponent[Filter.AndFilter]):

    class_name = "AndFilter"
    filter_class = Filter.AndFilter
    __slots__ = ()

class OrFilterComponent(MetaFilterComponent[Filter.OrFilter]):

    class_name = "OrFilter"
    filter_class = Filter.OrFilter
    __slots__ = ()

class NandFilterComponent(MetaFilterComponent[Filter.NandFilter]):

    class_name = "NandFilter"
    filter_class = Filter.NandFilter
    __slots__ = ()

class NorFilterComponent(MetaFilterComponent[Filter.NorFilter]):

    class_name = "NorFilter"
    filter_class = Filter.NorFilter
    __slots__ = ()

class EqFilterComponent(ValueFilterComponent[Filter.EqFilter]):

    class_name = "EqFilter"
    filter_class = Filter.EqFilter
    __slots__ = ()

class NeFilterComponent(ValueFilterComponent[Filter.NeFilter]):

    class_name = "NeFilter"
    filter_class = Filter.NeFilter
    __slots__ = ()

class GtFilterComponent(ValueFilterComponent[Filter.GtFilter]):

    class_name = "GtFilter"
    filter_class = Filter.GtFilter
    __slots__ = ()

class LtFilterComponent(ValueFilterComponent[Filter.LtFilter]):

    class_name = "LtFilter"
    filter_class = Filter.LtFilter
    __slots__ = ()

class GeFilterComponent(ValueFilterComponent[Filter.GeFilter]):

    class_name = "GeFilter"
    filter_class = Filter.GeFilter
    __slots__ = ()

class LeFilterComponent(ValueFilterComponent[Filter.LeFilter]):

    class_name = "LeFilter"
    filter_class = Filter.LeFilter
    __slots__ = ()
