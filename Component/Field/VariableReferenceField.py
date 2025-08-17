from types import EllipsisType
from typing import TYPE_CHECKING

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Field.FieldFactory import FieldFactory
    from Component.Field.Variable import Variable

class VariableReferenceField[R](Field[R]):

    __slots__ = (
        "propagating_variables",
        "result",
        "variable",
        "variable_name",
    )

    def __init__(self, factory: "FieldFactory", scope:Scope, error: Errors, variable_name:str) -> None:
        super().__init__(factory, scope, error)
        self.variable_name = variable_name
        self.variable:"Variable"
        self.result: R
        self.propagating_variables: PropagatingVariables|None

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and self.optional_scope == value.optional_scope and self.variable_name == value.variable_name

    def __hash__(self) -> int:
        return hash((type(self), self.optional_scope, self.variable_name))

    def create_field(self, memo: set["FieldFactory"], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if super().create_field(memo, trace) <= Errors.create_field:
                return self.error
            if (variable := self.scope.local_variables.get(self.variable_name)) is None:
                trace.exception(RuntimeError(f"Variable {self.variable_name} does not exist"))
                self.narrow(Errors.create_field)
            elif not variable.value_exists:
                trace.exception(RuntimeError(f"{self}, {self.variable_name} is not defined"))
                self.narrow(Errors.create_field)
            else:
                self.variable = variable
            return self.error
        return self.narrow(Errors.create_field)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        with trace.enter_field(self, ...):
            output, new_error = self.variable.get_final_type(trace)
            return output, self.narrow(new_error)
        return (), self.narrow(Errors.create_final)

    def link_final(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.linked_final: return self.result, self.propagating_variables, self.error
            self.linked_final = True
            result, propagating_variables, new_error = self.variable.link_final(trace)
            if self.narrow(new_error) <= Errors.link_final:
                return ..., None, self.error
            assert result is not ...
            self.result = result
            self.propagating_variables = propagating_variables
            return result, propagating_variables, self.error
        return ..., None, self.narrow(Errors.link_final)
