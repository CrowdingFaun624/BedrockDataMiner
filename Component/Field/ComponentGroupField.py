from typing import Callable, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Utilities.Exceptions as Exceptions


class ComponentGroupField[a: Component.Component](Field.Field):

    __slots__ = (
        "component_group",
        "component_group_name",
    )

    def __init__(self, component_group_name:str, path:list[str|int]) -> None:
        '''
        :component_group_name: The name of the Component group referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.component_group_name = component_group_name
        self.component_group:dict[str,a]|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list[Component.Component],list[Component.Component]]:
        component_group = cast(dict[str,a]|None, imported_components.get(self.component_group_name))
        if component_group is None:
            raise Exceptions.UnrecognizedComponentGroupError(self.component_group_name, repr(self))
        self.component_group = component_group
        return [], []

    def get_component_group(self) -> dict[str,a]:
        if self.component_group is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_component_group, self)
        return self.component_group
