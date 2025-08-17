from typing import NotRequired, Required, Sequence

from Component.Structure.StructureComponent import (
    StructureComponent,
    StructureTypedDict,
    tags_type_verifier,
    types_type_verifier,
)
from Structure.ConvergingStructure import ConvergingStructure
from Structure.Structure import Structure
from Structure.StructureTag import StructureTag
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class ConvergingStructureTypedDict(StructureTypedDict):
    end_structure: Required[Structure | None]
    structure: Required[Structure]
    tags: NotRequired[StructureTag | Sequence[StructureTag]]
    this_types: Required[type | Sequence[type]]
    within_structure_depth: Required[int]

class ConvergingStructureComponent(StructureComponent[ConvergingStructure, ConvergingStructureTypedDict]):

    type_name = "Converging"
    object_type = ConvergingStructure
    abstract = False

    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("end_structure", True, (Structure, type(None))),
        TypedDictKeyTypeVerifier("structure", True, Structure),
        TypedDictKeyTypeVerifier("tags", False, tags_type_verifier),
        TypedDictKeyTypeVerifier("this_types", True, types_type_verifier),
        TypedDictKeyTypeVerifier("within_structure_depth", True, int),
    ))

    def link_final(self, fields: ConvergingStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_converging_structure(
            end_structure=fields["end_structure"],
            structure=fields["structure"],
            tags=fields.get("tags", []),
            this_types=fields["this_types"],
            within_structure_depth=fields["within_structure_depth"],
        )
