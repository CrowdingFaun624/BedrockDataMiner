from typing import Any, Callable


class Function():
    '''Changes data before a Structure looks at it.'''

    __slots__ = (
        "arguments",
        "full_name",
        "function",
        "name",
        "trace_name",
    )

    def __init__(self, name:str, full_name:str, trace_name:str, function:Callable[[Any], Any], arguments:dict[str,Any]) -> None:
        '''
        :name: The Component name of this Function.
        :function: A Callable that **DOES NOT** modify the original object and returns nothing.
        :arguments: kwargs that are given to the function when this Function is called.
        '''
        self.name = name
        self.full_name = full_name
        self.trace_name = trace_name
        self.function = function
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def __call__(self, data:Any) -> Any:
        '''
        Calls the Function's function.
        :data: The argument of the Function's function.
        '''
        return self.function(data, **self.arguments)
