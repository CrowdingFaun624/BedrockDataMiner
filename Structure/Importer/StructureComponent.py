from typing import Generic, TypeVar

import Structure.Importer.Component as Component
import Structure.Structure as Structure
import Utilities.Exceptions as Exceptions

a = TypeVar("a", bound=Structure.Structure)

class StructureComponent(Component.Component, Generic[a]):

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"
    my_type:list[type]

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.final:a|None = None

    def get_final(self) -> a:
        if self.final is None:
            raise Exceptions.AttributeNoneError("final", self)
        return self.final
