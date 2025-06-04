from typing import Any, Callable

from Structure.Filter import Filter
from Structure.StructureInfo import StructureInfo


class Normalizer():
    '''Changes data before a Structure looks at it.'''

    __slots__ = (
        "arguments",
        "filter",
        "function",
        "name",
    )

    def __init__(self, name:str, function:Callable[[Any], Any], arguments:dict[str,Any]) -> None:
        '''
        :name: The Component name of this Normalizer.
        :function: A Callable that modifies the original object and returns nothing.
        :arguments: kwargs that are given to the function when this Normalizer is called.
        '''
        self.name = name
        self.function = function
        self.arguments = arguments
        self.filter:Filter|None = None

    def __repr__(self) -> str:
        function_name:str|None
        if hasattr(self.function, "__name__"):
            function_name = self.function.__name__
        elif hasattr(self.function, "name"):
            function_name = self.function.name
        else:
            function_name = None
        if function_name is None:
            return f"<{self.__class__.__name__} {self.name}>"
        else:
            return f"<{self.__class__.__name__} {self.name} {function_name}>"

    def link_subcomponents(self, filter:Filter|None) -> None:
        self.filter = filter

    def __call__(self, data:Any) -> Any:
        '''
        Calls the Normalizer's function.
        :data: The argument of the Normalizer's function.
        '''
        return self.function(data, **self.arguments)

    def filter_pass(self, structure_info:StructureInfo) -> bool:
        if self.filter is None:
            return True
        else:
            return self.filter.filter(structure_info)
