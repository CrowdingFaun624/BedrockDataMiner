import Component.Component as Component
import Component.Structure.StructureTagComponent as StructureTagComponent
import Structure.Structure as Structure


class StructureComponent[a: Structure.Structure](Component.Component[a]):

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"
    my_type:set[type]

    __slots__ = (
        "children_tags",
    )

    def get_propagated_variables(self) -> tuple[dict[str, bool], dict[str, set]]:
        self.children_tags:set[StructureTagComponent.StructureTagComponent] = set()
        return {"children_has_normalizer": False, "children_has_garbage_collection": False}, {"children_tags": self.children_tags}

    def finalize(self) -> list[Exception]:
        exceptions = super().finalize()
        delegate = self.final.delegate
        if delegate is not None:
            delegate.finalize()
        return exceptions
