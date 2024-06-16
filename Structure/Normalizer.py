from typing import Callable, Generic, TypeVar

IN = TypeVar("IN")
OUT = TypeVar("OUT")

class Normalizer(Generic[IN, OUT]):
    '''Changes data before a Structure looks at it.'''

    def __init__(self, function:Callable[[IN], OUT]):
        '''
        :function: A Callable that modifies the original object and returns nothing.
        '''
        self.function = function

    def __call__(self, data:IN) -> OUT|None:
        '''
        Calls the Normalizer's function.
        :data: The argument of the Normalizer's function.
        '''
        return self.function(data)
