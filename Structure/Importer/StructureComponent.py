from typing import TypeVar

import Structure.Importer.Component as Component
import Structure.Structure as Structure

a = TypeVar("a", bound=Structure.Structure)

class StructureComponent(Component.Component[a]):

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"
    my_type:list[type]

    def __init__(self, name: str) -> None:
        super().__init__(name)
