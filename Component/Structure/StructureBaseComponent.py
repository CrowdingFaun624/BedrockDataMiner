from typing import AbstractSet, Any, Mapping, NotRequired

from Component.Structure.BranchlessStructureComponent import (
    BranchlessStructureComponent,
    BranchlessStructureTypedDict,
)
from Structure.Delegate.Delegate import DelegateCreator
from Structure.StructureBase import StructureBase
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class StructureBaseTypedDict(BranchlessStructureTypedDict):
    delegate: NotRequired[DelegateCreator | None]

class StructureBaseComponent(BranchlessStructureComponent[StructureBase, StructureBaseTypedDict]):

    type_name = "StructureBase"
    object_type = StructureBase
    abstract = False

    type_verifier = BranchlessStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("delegate", False, (DelegateCreator, type(None))),
    ))

    def link_final(self, fields: StructureBaseTypedDict) -> None:
        super().link_final(fields)
        self.final.link_structure_base(
            delegate=fields.get("delegate", None),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        return self.final.finalize_structure_base(trace)
