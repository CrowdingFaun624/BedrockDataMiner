from typing import Any, Self

from Component.Component import INVALID_NAME_CHARS, Component
from Component.Expression.Expression import Expression, Reader
from Component.Expression.Variable import Variable
from Utilities.Exceptions import ExpressionParseError


class SubstituteExpression(Expression):
    '''
    Simple Expression type that simply dereferences a single Variable.
    '''

    __slots__ = (
        "is_key",
        "variable_name",
    )

    def __init__(self, source_component: Component, is_key:bool, variable_name:str) -> None:
        super().__init__(source_component, variable_name)
        self.is_key = is_key
        self.variable_name = variable_name
        self.variables_used.append(variable_name)

    def copy(self, new_component: Component) -> "SubstituteExpression":
        output = SubstituteExpression(self.source_component, self.is_key, self.variable_name)
        self.copy_attrs(output, new_component)
        return output

    def evaluate(self, variables: dict[str, Variable]) -> Any:
        return str(variables[self.variable_name].dereference(variables)) if self.is_key else variables[self.variable_name].dereference(variables)

    @classmethod
    def applicable(cls, reader: Reader, is_key: bool) -> bool:
        return reader.read(1) not in INVALID_NAME_CHARS

    @classmethod
    def parse(cls, reader: Reader, source_component: Component, is_key: bool) -> Self:
        name_string = reader.read_while(lambda char: char not in INVALID_NAME_CHARS)
        if not Variable.name_is_valid(name_string):
            raise ExpressionParseError(reader, cls, f"because {name_string} is not a valid Variable name")
        return cls(source_component, is_key, name_string)
