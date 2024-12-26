from typing import TypeVar

import Component.Component as Component
import Structure.Structure as Structure

a = TypeVar("a", bound=Structure.Structure)

class StructureComponent(Component.Component[a]):

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"
    my_type:set[type]

    def finalize(self) -> None:
        super().finalize()
        delegate = self.get_final().delegate
        if delegate is not None:
            delegate.finalize()
