from typing import NotRequired, TypedDict

from Component.Component import Component
from Structure.StructureTag import StructureTag
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class StructureTagTypedDict(TypedDict):
    is_file: NotRequired[bool]

class StructureTagComponent(Component[StructureTag, StructureTagTypedDict]):

    type_name = "StructureTag"
    object_type = StructureTag
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("is_file", False, bool),
    ))

    def get_propagating_variables(self) -> tuple[dict[str, bool], dict[str, set[object]]]:
        return {}, {"children_tags": {self.final}}

    def link_final(self, fields: StructureTagTypedDict) -> None:
        super().link_final(fields)
        self.final.link_structure_tag(
            is_file=fields.get("is_file", False)
        )
