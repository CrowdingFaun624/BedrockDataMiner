from types import EllipsisType
from typing import Any, Hashable, Self, cast

import Component.Component as Component
import Component.Expression.Expression as Expression
from Utilities.Exceptions import VariableDereferenceError, VariableNameError


class Variable[T]():

    __slots__ = (
        "expressions",
        "name",
        "value",
    )

    @staticmethod
    def name_is_valid(name:str) -> bool:
        return not (len(name) == 0 or any(char in Component.INVALID_NAME_CHARS for char in name) or name in Component.INVALID_NAMES or Component.is_number(name))

    def __init__(
            self,
            name:str,
            value:T|EllipsisType=..., # type: ignore why do you do this
        ) -> None:
        self.name:str = name
        self.value:T|EllipsisType = value
        '''
        The value contained by this Variable. May be undefined (Ellipsis).
        '''
        if not self.name_is_valid(self.name):
            raise VariableNameError(self.name)

    @property
    def undefined(self) -> bool:
        return self.value is ...

    def dereference(self, variables:dict[str,"Variable"]) -> T:
        if self.value is ...:
            raise VariableDereferenceError(self)
        if isinstance(self.value, Expression.Expression):
            value:T = self.value.evaluate(variables)
            self.value = value
        return self.value

    def set_value(self, value:T) -> Self:
        self.value = value
        return self

    def copy(self, new_component:"Component.Component") -> "Variable[T]":
        '''
        Creates a copy of this Variable. Does not copy the value unless the value
        is an Expression.
        '''
        new_value:T|EllipsisType = cast(T, self.value.copy(new_component)) if isinstance(self.value, Expression.Expression) else self.value
        return Variable(self.name, new_value)

    def __repr__(self) -> str:
        if self.value is ...:
            return f"<{self.__class__.__name__} {self.name}: undefined>"
        else:
            return f"<{self.__class__.__name__} {self.name}: {repr(self.value)}>"

    def __hash__(self) -> int:
        return hash((self.name, self.value))

def hash_data(data:Any) -> Hashable:
    match data:
        case str(): return data
        case dict(): return (dict, *((hash_data(key), hash_data(value)) for key, value in data.items()))
        case list(): return (list, *(hash_data(item) for item in data))
        case _: return data
