from typing import AbstractSet, Any, Mapping, NotRequired, Required, Sequence, TypedDict

from Component.Component import Component
from Component.Structure.StructureComponent import (
    tags_type_verifier,
    types_type_verifier,
)
from Structure.Filter import Filter
from Structure.Key import Key
from Structure.Structure import Structure
from Structure.StructureTag import StructureTag
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class KeyTypedDict(TypedDict):
    delegate_arguments: NotRequired[Mapping[str,Any]]
    filter: NotRequired[Filter | None]
    required: NotRequired[bool]
    similarity_weight: NotRequired[int]
    structure: NotRequired[Structure|None]
    tags: NotRequired[StructureTag | Sequence[StructureTag]]
    types: Required[type | Sequence[type]]
    value_weight: NotRequired[int | None]

class KeyComponent(Component[Key, KeyTypedDict]):

    type_name = "Key"
    object_type = Key
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("delegate_arguments", False, DictTypeVerifier(dict, str, object)),
        TypedDictKeyTypeVerifier("filter", False, (Filter, type(None))),
        TypedDictKeyTypeVerifier("required", False, bool),
        TypedDictKeyTypeVerifier("similarity_weight", False, int),
        TypedDictKeyTypeVerifier("structure", False, (Structure, type(None))),
        TypedDictKeyTypeVerifier("tags", False, tags_type_verifier),
        TypedDictKeyTypeVerifier("types", True, types_type_verifier),
        TypedDictKeyTypeVerifier("value_weight", False, (int, type(None))),
    ))

    def link_final(self, fields: KeyTypedDict) -> None:
        super().link_final(fields)
        self.final.link_key(
            delegate_arguments=fields.get("delegate_arguments", None),
            filter=fields.get("filter", None),
            required=fields.get("required", False),
            similarity_weight=fields.get("similarity_weight", 1),
            structure=fields.get("structure", None),
            tags=fields.get("tags", ()),
            types=fields["types"],
            value_weight=fields.get("value_weight", None)
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_key()
        return False
