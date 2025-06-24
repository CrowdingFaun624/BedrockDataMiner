from itertools import chain
from typing import Iterable

from Component.Component import Component
from Component.Expression.Expression import Expression


class ExpressionContainer(Expression):

    def __init__(self, source_component: Component, source:str|None=None) -> None:
        super().__init__(source_component, source)
        self.expressions:list[Expression] = []

    def copy(self, new_component: Component) -> "ExpressionContainer":
        output = ExpressionContainer(self.source_component)
        self.copy_attrs(output, new_component)
        return output
        # `expressions` is to be refilled by subclasses.

    def get_variables_used(self) -> Iterable[str]:
        yield from super().get_variables_used()
        yield from chain.from_iterable(expression.get_variables_used() for expression in self.expressions)
