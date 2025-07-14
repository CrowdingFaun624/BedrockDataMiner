from itertools import chain
from typing import Hashable, Iterable, Sequence

from Component.Component import Component
from Component.Expression.Expression import Expression
from Component.Expression.Variable import Variable


class ContainerExpression(Expression):

    __slots__ = (
        "subexpressions",
    )

    def __init__(self, source_component: Component, source:str, subexpressions:Sequence[Expression]) -> None:
        super().__init__(source_component, source)
        self.subexpressions:Sequence[Expression] = subexpressions

    def copy(self, new_component: Component) -> "ContainerExpression":
        output = ContainerExpression(self.source_component, self.source, ())
        self.copy_attrs(output, new_component)
        return output
        # `expressions` is to be refilled by subclasses.

    def get_variables_used(self, variables:dict[str,"Variable"]) -> Iterable[str]:
        yield from chain.from_iterable(expression.get_variables_used(variables) for expression in self.subexpressions)

    def __hash__(self) -> int: # it is important that sub-Expressions are hashed.
        hashable_thing:list[Hashable] = [super().__hash__()]
        hashable_thing.extend(hash(expression) for expression in self.subexpressions)
        return hash(tuple(hashable_thing))

