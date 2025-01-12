from typing import Callable

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Utilities.Exceptions as Exceptions


class FunctionField(Field.Field):

    __slots__ = (
        "function",
        "function_name",
    )

    def __init__(self, function_name:str, path:list[str|int], ignore_parameters:set[str]|None=None) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        function = functions.get(self.function_name)
        if function is None:
            raise Exceptions.ComponentUnrecognizedFunctionError(self.function_name, source_component)
        self.function = function
        return [], []
