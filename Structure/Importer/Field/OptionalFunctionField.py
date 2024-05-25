from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.Field.Field as Field

if TYPE_CHECKING:
    import Structure.Importer.Component as Component

class OptionalFunctionField(Field.Field):

    def __init__(self, function_name:str|None, path:list[str|int]) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable|None = None
        self.has_set_function = False

    def set(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        self.has_set_function = True
        if self.function_name is None:
            self.function = None
        else:
            function = functions.get(self.function_name)
            if function is None:
                raise KeyError("Function \"%s\" does not exist in %s \"%s\"!" % (self.function_name, component_class_name, component_name))
            self.function = function
        return []

    def get_function(self) -> Callable|None:
        '''
        Returns the function this Field refers to.
        Can only be called after `set`.
        '''
        if not self.has_set_function:
            raise RuntimeError("Cannot call `get_function` before `set`!")
        return self.function
