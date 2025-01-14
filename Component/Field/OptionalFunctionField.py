from typing import TYPE_CHECKING, Callable

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter

if TYPE_CHECKING:
    import Component.Component as Component

class OptionalFunctionField(Field.Field):

    __slots__ = (
        "function",
        "function_name",
    )

    def __init__(self, function_name:str|None, path:list[str|int], ignore_parameters:set[str]|None=None) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        if self.function_name is None:
            self.function = None
        else:
            self.function = functions.callables.get(self.function_name, source_component, self.error_path)
        return [], []
