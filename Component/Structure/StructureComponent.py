from typing import Any

import Component.Component as Component
import Component.Pattern as Pattern
import Component.Structure.StructureTagComponent as StructureTagComponent
import Domain.Domain as Domain
import Structure.Structure as Structure

STRUCTURE_COMPONENT_PATTERN:Pattern.Pattern["StructureComponent[Structure.Structure]"] = Pattern.Pattern("is_structure")

class StructureComponent[a: Structure.Structure](Component.Component[a]):

    class_name = "StructureComponent"

    __slots__ = (
        "children_tags",
        "my_type",
    )

    def __init__(self, data: Any, name: str, domain: "Domain.Domain", component_group: str, index: int | None) -> None:
        self.my_type:set[type] = set()
        super().__init__(data, name, domain, component_group, index)

    def get_propagated_variables(self) -> tuple[dict[str, bool], dict[str, set]]:
        self.children_tags:set[StructureTagComponent.StructureTagComponent] = set()
        return {"children_has_normalizer": False, "children_has_garbage_collection": False}, {"children_tags": self.children_tags}

    def finalize(self) -> list[Exception]:
        exceptions = super().finalize()
        delegate = self.final.delegate
        if delegate is not None:
            delegate.finalize()
        return exceptions
