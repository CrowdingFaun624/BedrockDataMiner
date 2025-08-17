from typing import AbstractSet, Any, Mapping, Required, Sequence

from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
    PassthroughStructureTypedDict,
)
from Component.Structure.StructureComponent import types_type_verifier
from Structure.BranchlessStructure import BranchlessStructure
from Structure.Structure import Structure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class BranchlessStructureTypedDict(PassthroughStructureTypedDict):
    structure: Required[Structure | None]
    this_types: Required[type | Sequence[type]]


class BranchlessStructureComponent[R: BranchlessStructure, P: BranchlessStructureTypedDict](PassthroughStructureComponent[R, P]):

    type_name = "Branchless"
    object_type = BranchlessStructure
    abstract = True

    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("structure", True, (Structure, type(None))),
        TypedDictKeyTypeVerifier("this_types", True, types_type_verifier),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_branchless_structure(
            structure=fields["structure"],
            this_types=fields["this_types"],
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        self.final.finalize_branchless_structure()
        return super().finalize(propagating_booleans, propagating_sets, trace)
