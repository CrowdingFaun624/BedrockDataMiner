from typing import AbstractSet, Any, Mapping, Required, Sequence

from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
    PassthroughStructureTypedDict,
)
from Structure.Key import Key
from Structure.StructureTypes.UnionStructure import UnionStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class UnionStructureTypedDict(PassthroughStructureTypedDict):
    substructures: Required[Sequence[Key]]

class UnionStructureComponent(PassthroughStructureComponent[UnionStructure, UnionStructureTypedDict]):

    type_name = "Union"
    object_type = UnionStructure
    abstract = False

    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("substructures", True, ListTypeVerifier(Key, list)),
    ))

    def link_final(self, fields: UnionStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_union_structure(
            keys=fields["substructures"],
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_union_structure()
        return False
