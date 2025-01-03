import Component.Component as Component
import Structure.Structure as Structure


class StructureComponent[a: Structure.Structure](Component.Component[a]):

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"
    my_type:set[type]

    __slots__ = ()

    def finalize(self) -> None:
        super().finalize()
        delegate = self.get_final().delegate
        if delegate is not None:
            delegate.finalize()
