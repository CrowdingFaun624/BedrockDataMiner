from typing import AbstractSet, Any, Mapping, NotRequired, Required, Sequence

from Component.Structure.StructureComponent import (
    StructureComponent,
    StructureTypedDict,
    tags_type_verifier,
    types_type_verifier,
)
from Structure.Structure import Structure
from Structure.StructureTag import StructureTag
from Structure.WithinStructure import WithinStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class WithinStructureTypedDict(StructureTypedDict):
    inner_types: Required[type | Sequence[type]]
    outer_types: Required[type | Sequence[type]]
    structure: Required[Structure]
    tags: NotRequired[StructureTag | Sequence[StructureTag]]

class WithinStructureComponent[R: WithinStructure, P: WithinStructureTypedDict](StructureComponent[R, P]):

    type_name = "Within"
    object_type = WithinStructure
    abstract = True

    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("inner_types", True, types_type_verifier),
        TypedDictKeyTypeVerifier("outer_types", True, types_type_verifier),
        TypedDictKeyTypeVerifier("structure", True, Structure),
        TypedDictKeyTypeVerifier("tags", False, tags_type_verifier)
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_within_structure(
            inner_types=fields["inner_types"],
            outer_types=fields["outer_types"],
            structure=fields["structure"],
            tags=fields.get("tags", ()),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_within_structure()
        return False
