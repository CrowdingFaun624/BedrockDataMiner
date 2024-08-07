from typing import TYPE_CHECKING, Any, Callable

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.FunctionChecker as FunctionChecker
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component

class FunctionField(Field.Field):

    def __init__(self, function_name:str, path:list[str|int]) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable|None = None
        self.arguments_to_check:dict[str,Any] = {}
        self.ignore_parameters:set[str] = set()

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

    def check_arguments(self, arguments:dict[str,Any], ignore_parameters:set[str]|None=None) -> None:
        self.arguments_to_check = arguments
        if ignore_parameters is not None:
            self.ignore_parameters = ignore_parameters

    def get_function(self) -> Callable:
        '''
        Returns the function this Field refers to.
        Can only be called after `set_field`.
        '''
        if self.function is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_function, self)
        return self.function

    def check(self, source_component: Component.Component) -> list[Exception]:
        exceptions = super().check(source_component)
        exceptions.extend(FunctionChecker.check(self.get_function(), self.arguments_to_check, self.ignore_parameters, source_component))
        return exceptions
