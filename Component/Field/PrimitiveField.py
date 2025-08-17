from types import EllipsisType

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace


class PrimitiveField[R](Field[R]):

    __slots__ = (
        "value",
    )

    requires_variables = False

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, value:R) -> None:
        super().__init__(factory, scope, error)
        self.value = value

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and self.value == value.value

    def __hash__(self) -> int:
        return hash((type(self), self.value))

    def get_final_type(self, memo: set[FieldFactory], trace: Trace) -> tuple[tuple[type, ...], Errors]:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            return ((type(self.value),), self.error)
        return (), self.narrow(Errors.create_final)

    def link_final(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            self.linked_final = True
            return self.value, None, self.error
        return ..., None, self.narrow(Errors.link_final)
