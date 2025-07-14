from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import StructureTypedDict
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Component.Structure.StructureTagComponent import StructureTagComponent
from Structure.Structure import Structure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

STRUCTURE_COMPONENT_PATTERN:Pattern["StructureComponent[Structure]"] = Pattern("is_structure")

class StructureComponent[a: Structure](Component[a]):

    class_name = "StructureComponent"
    my_capabilities = Capabilities(is_structure=True)
    structure_type:type[a]
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("type", False, str),
    )
    script_referenceable = True

    __slots__ = (
        "children_tags",
        "my_type",
    )

    def initialize_fields(self, data: StructureTypedDict) -> Sequence[Field]:
        self.my_type:set[type] = set()
        return super().initialize_fields(data)

    def create_final(self, trace:Trace) -> a:
        return self.structure_type(
            name=self.name,
            full_name=self.full_name,
            is_inline=self.index is None,
            trace_name=self.trace_name,
        )

    def link_finals(self, trace: Trace) -> None:
        self.final.link_structure(
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_tags={tag.final for tag in self.children_tags},
        )

    def get_propagated_variables(self) -> tuple[dict[str, bool], dict[str, set]]:
        self.children_tags:set[StructureTagComponent] = set()
        return {"children_has_normalizer": False, "children_has_garbage_collection": False, "children_has_version_domains": False}, {"children_tags": self.children_tags}
