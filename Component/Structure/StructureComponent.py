import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Pattern as Pattern
import Component.Structure.StructureTagComponent as StructureTagComponent
import Domain.Domain as Domain
import Structure.Structure as Structure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

STRUCTURE_COMPONENT_PATTERN:Pattern.Pattern["StructureComponent[Structure.Structure]"] = Pattern.Pattern("is_structure")

class StructureComponent[a: Structure.Structure](Component.Component[a]):

    class_name = "StructureComponent"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    structure_type:type[a]
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )
    script_referenceable = True

    __slots__ = (
        "children_tags",
        "my_type",
    )

    def __init__(self, data: ComponentTyping.StructureTypedDict, name: str, domain: "Domain.Domain", component_group: str, index: int | None, trace:Trace.Trace) -> None:
        self.my_type:set[type] = set()
        super().__init__(data, name, domain, component_group, index, trace)

    def create_final(self, trace:Trace.Trace) -> a:
        return self.structure_type(
            name=self.name,
            full_name=self.full_name,
        )

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_structure(
                children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
                children_has_normalizer=self.variable_bools["children_has_normalizer"],
                children_tags={tag.final for tag in self.children_tags},
            )

    def get_propagated_variables(self) -> tuple[dict[str, bool], dict[str, set]]:
        self.children_tags:set[StructureTagComponent.StructureTagComponent] = set()
        return {"children_has_normalizer": False, "children_has_garbage_collection": False}, {"children_tags": self.children_tags}
