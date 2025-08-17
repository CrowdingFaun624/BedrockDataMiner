from typing import AbstractSet, Any, Mapping, NotRequired

from Component.Structure.BranchlessStructureComponent import (
    BranchlessStructureComponent,
    BranchlessStructureTypedDict,
)
from Structure.Delegate.Delegate import DelegateCreator
from Structure.StructureTypes.CacheStructure import CacheStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class CacheStructureTypedDict(BranchlessStructureTypedDict):
    delegate: NotRequired[DelegateCreator | None]
    removal_threshold: NotRequired[bool]

class CacheStructureComponent(BranchlessStructureComponent[CacheStructure, CacheStructureTypedDict]):

    type_name = "Cache"
    object_type = CacheStructure
    abstract = False

    type_verifier = BranchlessStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("removal_threshold", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypedDictKeyTypeVerifier("delegate", False, (DelegateCreator, type(None))),
    ))

    def link_final(self, fields: CacheStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_cache_structure(
            delegate=fields.get("delegate", None),
            removal_threshold=fields.get("removal_threshold", 2),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        return self.final.finalize_cache_structure(propagating_booleans["cache_versions_for_delegates"], trace)
