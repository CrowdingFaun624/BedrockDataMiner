from typing import AbstractSet, Any, Mapping, NotRequired, Sequence

from Component.Structure.StructureComponent import (
    StructureComponent,
    StructureTypedDict,
    tags_type_verifier,
)
from Structure.PassthroughStructure import PassthroughStructure
from Structure.StructureTag import StructureTag
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class PassthroughStructureTypedDict(StructureTypedDict):
    tags: NotRequired[StructureTag | Sequence[StructureTag]]

class PassthroughStructureComponent[R: PassthroughStructure, P: PassthroughStructureTypedDict](StructureComponent[R, P]):

    type_name = "Passthrough"
    object_type = PassthroughStructure
    abstract = True

    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("tags", False, tags_type_verifier),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_passthrough_structure(
            tags=fields.get("tags", []),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_passthrough_structure()
        return False
