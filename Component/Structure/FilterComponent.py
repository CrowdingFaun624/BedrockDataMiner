from typing import NotRequired, Required, Sequence, TypedDict

from Component.Component import Component
from Structure.Filter import (
    AndFilter,
    EqFilter,
    Filter,
    GeFilter,
    GtFilter,
    KeyFilter,
    KeyNotPresentFilter,
    KeyPresentFilter,
    LeFilter,
    LtFilter,
    MetaFilter,
    NandFilter,
    NeFilter,
    NorFilter,
    OrFilter,
    ValueFilter,
)
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class FilterTypedDict(TypedDict):
    pass # empty

class FilterComponent[R: Filter, P: FilterTypedDict=FilterTypedDict](Component[R, P]):

    type_name = "Filter"
    object_type = Filter
    abstract = True

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_filter()

class ValueFilterTypedDict(FilterTypedDict):
    default: NotRequired[bool]
    key: Required[str]
    value: Required[object]

class ValueFilterComponent[R: ValueFilter, P: ValueFilterTypedDict=ValueFilterTypedDict](FilterComponent[R, P]):

    type_name = "ValueFilter"
    object_type = ValueFilter
    abstract = True

    type_verifier = FilterComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("default", False, bool),
        TypedDictKeyTypeVerifier("key", False, str),
        TypedDictKeyTypeVerifier("value", False, object),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_value_filter(
            default=fields.get("default", False),
            key=fields["key"],
            value=fields["value"],
        )

class KeyFilterTypedDict(FilterTypedDict):
    key: Required[str]

class KeyFilterComponent[R: KeyFilter, P: KeyFilterTypedDict=KeyFilterTypedDict](FilterComponent[R, P]):

    type_name = "KeyFilter"
    object_type = KeyFilter
    abstract = True

    type_verifier = FilterComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("key", True, str),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_key_filter(
            key=fields["key"],
        )

class MetaFilterTypedDict(FilterTypedDict):
    subfilters: Sequence[Filter]

class MetaFilterComponent[R: MetaFilter, P: MetaFilterTypedDict=MetaFilterTypedDict](FilterComponent[R, P]):

    type_name = "MetaFilter"
    object_type = MetaFilter
    abstract = True

    type_verifier = FilterComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("subfilters", True, ListTypeVerifier(Filter, list)),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_meta_filter(
            subfilters=fields["subfilters"],
        )

class KeyPresentFilterComponent(KeyFilterComponent[KeyPresentFilter]):

    type_name = "KeyPresentFilter"
    object_type = KeyPresentFilter
    abstract = False

class KeyNotPresentFilterComponent(KeyFilterComponent[KeyNotPresentFilter]):

    type_name = "KeyNotPresentFilter"
    object_type = KeyNotPresentFilter
    abstract = False

class AndFilterComponent(MetaFilterComponent[AndFilter]):

    type_name = "AndFilter"
    object_type = AndFilter
    abstract = False

class OrFilterComponent(MetaFilterComponent[OrFilter]):

    type_name = "OrFilter"
    object_type = OrFilter
    abstract = False

class NandFilterComponent(MetaFilterComponent[NandFilter]):

    type_name = "NandFilter"
    object_type = NandFilter
    abstract = False

class NorFilterComponent(MetaFilterComponent[NorFilter]):

    type_name = "NorFilter"
    object_type = NorFilter
    abstract = False

class EqFilterComponent(ValueFilterComponent[EqFilter]):

    type_name = "EqFilter"
    object_type = EqFilter
    abstract = False

class NeFilterComponent(ValueFilterComponent[NeFilter]):

    type_name = "NeFilter"
    object_type = NeFilter
    abstract = False

class GtFilterComponent(ValueFilterComponent[GtFilter]):

    type_name = "GtFilter"
    object_type = GtFilter
    abstract = False

class LtFilterComponent(ValueFilterComponent[LtFilter]):

    type_name = "LtFilter"
    object_type = LtFilter
    abstract = False

class GeFilterComponent(ValueFilterComponent[GeFilter]):

    type_name = "GeFilter"
    object_type = GeFilter
    abstract = False

class LeFilterComponent(ValueFilterComponent[LeFilter]):

    type_name = "LeFilter"
    object_type = LeFilter
    abstract = False
