from typing import TYPE_CHECKING, Callable, Sequence

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.Field import Field
from Component.Field.FieldContainer import FieldContainer
from Component.ScriptImporter import ScriptSetSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class FunctionField(Field):

    __slots__ = (
        "function",
        "function_name",
    )

    def __init__(self, function_name:str, path:tuple[str,...]) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:dict[str,dict[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["Component"],Sequence["Component"]]:
        with trace.enter_keys(self.trace_path, self.function_name):
            function = functions.callables.get(self.function_name, source_component)
            self.function = function
            return (), ()
        return (), ()

class OptionalFunctionField(FieldContainer):

    __slots__ = (
        "function_field",
    )

    def __init__(self, function_name:str|None, path:tuple[str,...]) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        self.function_field:FunctionField|None
        if function_name is None:
            self.function_field = None
            super().__init__([], path)
        else:
            self.function_field = FunctionField(function_name, path)
            super().__init__([self.function_field], path)

    @property
    def function(self) -> Callable|None:
        return None if self.function_field is None else self.function_field.function

    @property
    def exists(self) -> bool:
        return self.function_field is not None
