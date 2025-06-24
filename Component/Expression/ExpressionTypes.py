from typing import Sequence

from Component.Expression.ComponentResolveExpression import ComponentResolveExpression
from Component.Expression.Expression import Expression
from Component.Expression.SubstituteExpression import SubstituteExpression
from Component.Expression.VariableReferenceExpression import VariableReferenceExpression

expression_types:Sequence[type[Expression]] = [ # sorted in order of parsing priority; most to least.
    SubstituteExpression,
    ComponentResolveExpression,
    VariableReferenceExpression,
]
