from typing import Any, Sequence

from Component.Component import Component
from Component.Expression.ContainerExpression import ContainerExpression
from Component.Expression.Expression import Expression
from Component.Expression.Variable import Variable
from Component.Field.Field import resolve_reference


class ComponentExpression(ContainerExpression):

    __slots__ = (
        "component_name",
        "direct",
        "variables",
    )

    def __init__(self, source_component: Component, source:str, subexpressions:Sequence[Expression], component_name:str, direct:bool, variables:dict[str,Any]|None) -> None:
        super().__init__(source_component, source, subexpressions)
        self.component_name = component_name
        self.direct = direct
        self.variables:dict[str,Any]|None = variables

    def copy(self, new_component: Component) -> "ComponentExpression":
        output = ComponentExpression(self.source_component, self.source, (), self.component_name, self.direct, None)
        self.copy_attrs(output, new_component)
        return output

    def copy_attrs(self, new_expression: "ComponentExpression", new_component: Component) -> None:
        super().copy_attrs(new_expression, new_component)
        if self.variables is not None:
            new_expression.variables = {key: (value.copy(new_component) if isinstance(value, Expression) else value) for key, value in self.variables.items()}
            new_expression.subexpressions = [value for value in new_expression.variables.values() if isinstance(value, Expression)]

    def evaluate(self, variables:dict[str,Variable]) -> dict[str,int|float|str|bool|None]|str:
        component_name = resolve_reference(self.component_name, self.source_component.group) if self.direct else self.component_name
        if self.variables is None or len(self.variables) == 0:
            return component_name
        else:
            output:dict[str,Any] = {
                "inherit": component_name,
                "inheritance_type": "reference",
            } | {"$" + key: value.evaluate(variables) if isinstance(value, Expression) else value for key, value in self.variables.items()}
            output.update()
            return output
