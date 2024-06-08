from typing import Any, TypeVar

import Component.Component as Component
import Structure.Structure as Structure

a = TypeVar("a", bound=Structure.Structure)

class AbstractGroupComponent(Component.Component[dict[type,a|None]]):

    def __init__(self, data:Any, name: str, component_group: str) -> None:
        super().__init__(data, name, component_group)
        self.my_type:set[type] = set()

    def get_subcomponents(self) -> list[Component.Component]:
        '''
        Returns a list of this Component's subcomponents.
        '''
        ...
