from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.Field.Field as Field
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Importer.Component as Component

class FunctionField(Field.Field):

    def __init__(self, function_name:str, path:list[str|int]) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable|None = None

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        function = functions.get(self.function_name)
        if function is None:
            raise Exceptions.ComponentUnrecognizedFunctionError(self.function_name, "%s \"%s\"" % (component_class_name, component_name))
        self.function = function
        return []

    def get_function(self) -> Callable:
        '''
        Returns the function this Field refers to.
        Can only be called after `set_field`.
        '''
        if self.function is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_function, self)
        return self.function
