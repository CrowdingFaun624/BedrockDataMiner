from typing import Any, Self

from Component.Component import INVALID_NAME_CHARS, Component
from Component.Expression.Expression import Expression, Reader
from Component.Expression.Variable import Variable
from Component.Field.Field import resolve_reference
from Utilities.Exceptions import ExpressionParseError


class ComponentResolveExpression(Expression):
    '''
    Simple Expression type that simply dereferences a single Variable.
    '''

    __slots__ = (
        "component_name",
        "is_key",
    )

    def __init__(self, source_component: Component, is_key:bool, component_name:str) -> None:
        super().__init__(source_component, "@" + component_name)
        self.is_key = is_key
        self.component_name = component_name

    def copy(self, new_component: Component) -> "ComponentResolveExpression":
        output = ComponentResolveExpression(self.source_component, self.is_key, self.component_name)
        self.copy_attrs(output, new_component)
        return output

    def evaluate(self, variables: dict[str, Variable]) -> Any:
        return resolve_reference(self.component_name, self.source_component.group)

    @classmethod
    def applicable(cls, reader: Reader, is_key: bool) -> bool:
        return reader.read(1) == "@"

    @classmethod
    def parse(cls, reader: Reader, source_component: Component, is_key: bool) -> Self:
        if reader.read(1) != "@":
            raise ExpressionParseError(reader, cls, f"b")
        name_string = reader.read_while(lambda char: char not in INVALID_NAME_CHARS)
        return cls(source_component, is_key, name_string)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.component_name}>"

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.source_component.group))
