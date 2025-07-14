from typing import Any

from Component.Component import Component
from Component.Expression.ContainerExpression import ContainerExpression
from Component.Expression.Expression import Expression
from Component.Expression.Variable import Variable


class ConcatenationExpression(ContainerExpression):

    __slots__ = (
        "item1",
        "item2",
    )

    def __init__(self, source_component: Component, source: str, item1:Any, item2:Any) -> None:
        super().__init__(source_component, source, (item1, item2))
        self.item1 = item1
        self.item2 = item2

    def copy(self, new_component: Component) -> ContainerExpression:
        item1 = self.item1.copy(new_component) if isinstance(self.item1, Expression) else self.item1
        item2 = self.item2.copy(new_component) if isinstance(self.item2, Expression) else self.item2
        output = ConcatenationExpression(self.source_component, self.source, item1, item2)
        self.copy_attrs(output, new_component)
        return output

    def evaluate(self, variables: dict[str, Variable]) -> Any:
        item1 = self.item1.evaluate(variables) if isinstance(self.item1, Expression) else self.item1
        item2 = self.item2.evaluate(variables) if isinstance(self.item2, Expression) else self.item2
        return item1 + item2
