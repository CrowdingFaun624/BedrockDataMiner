from typing import AbstractSet, Any, Mapping, NotRequired, Sequence

from Component.Structure.StructureComponent import (
    StructureComponent,
    StructureTypedDict,
    tags_type_verifier,
    types_type_verifier,
)
from Structure.Delegate.Delegate import DelegateCreator
from Structure.PrimitiveStructure import PrimitiveStructure
from Structure.StructureTag import StructureTag
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class PrimitiveStructureTypedDict(StructureTypedDict):
    delegate: NotRequired[DelegateCreator | None]
    tags: NotRequired[StructureTag | Sequence[StructureTag]]
    this_types: NotRequired[type | Sequence[type]]

class PrimitiveStructureComponent[R: PrimitiveStructure=PrimitiveStructure, P: PrimitiveStructureTypedDict=PrimitiveStructureTypedDict](StructureComponent[R, P]):

    type_name = "Primitive"
    object_type = PrimitiveStructure
    abstract = False # not abstract but still has subclasses.

    default_types:tuple[type,...] = ()
    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("delegate", False, (DelegateCreator, type(None))),
        TypedDictKeyTypeVerifier("tags", False, tags_type_verifier),
        TypedDictKeyTypeVerifier("this_types", False, types_type_verifier),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_primitive_structure(
            delegate=fields.get("delegate", None),
            tags=fields.get("tags", []),
            this_types=fields.get("this_types", self.default_types),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        return self.final.finalize_primitive_structure(trace) or super().finalize(propagating_booleans, propagating_sets, trace)
