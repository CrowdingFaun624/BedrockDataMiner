from typing import TYPE_CHECKING, Callable

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component

class OptionalFunctionField(Field.Field):

    def __init__(self, function_name:str|None, path:list[str|int]) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable|None = None
        self.has_set_function = False

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        self.has_set_function = True
        if self.function_name is None:
            self.function = None
        else:
            function = functions.get(self.function_name)
            if function is None:
                raise Exceptions.ComponentUnrecognizedFunctionError(self.function_name, source_component)
            self.function = function
        return [], []

    def get_function(self) -> Callable|None:
        '''
        Returns the function this Field refers to.
        Can only be called after `set_field`.
        '''
        if not self.has_set_function:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_function, self)
        return self.function
