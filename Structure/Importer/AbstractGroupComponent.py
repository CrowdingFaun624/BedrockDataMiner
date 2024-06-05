from typing import TypeVar

import Structure.Importer.Component as Component
import Structure.Structure as Structure

a = TypeVar("a", bound=Structure.Structure)

class AbstractGroupComponent(Component.Component[dict[type,a|None]]):

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.my_type:set[type] = set()

    def get_subcomponents(self) -> list[Component.Component]:
        '''
        Returns a list of this Component's subcomponents.
        '''
        ...
