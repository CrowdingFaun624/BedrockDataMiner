from typing import Any, Iterable

from Component.Component import Component
from Component.Expression.Expression import Expression
from Component.Expression.Variable import Variable


class VariableExpression(Expression):
    '''
    Expression type that simply dereferences a single Variable.
    '''

    __slots__ = (
        "is_key",
        "variable_name",
    )

    def __init__(self, source_component: Component, source:str, is_key:bool, variable_name:str) -> None:
        super().__init__(source_component, source)
        self.is_key = is_key
        self.variable_name = variable_name

    def copy(self, new_component: Component) -> "VariableExpression":
        output = VariableExpression(self.source_component, self.source, self.is_key, self.variable_name)
        self.copy_attrs(output, new_component)
        return output

    def evaluate(self, variables: dict[str, Variable]) -> Any:
        return str(variables[self.variable_name].dereference(variables)) if self.is_key else variables[self.variable_name].dereference(variables)

    def get_variables_used(self, variables:dict[str,"Variable"]) -> Iterable[str]:
        yield self.variable_name
        yield from variables[self.variable_name].get_variables_used(variables)
