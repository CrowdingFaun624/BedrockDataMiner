from types import EllipsisType

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace


class TypeField[T](Field[type[T]]):

    __slots__ = (
        "type_name",
        "type_result",
    )

    requires_variables = False

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, type_name:str) -> None:
        super().__init__(factory, scope, error)
        self.type_name = type_name
        self.type_result:type[T]

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and self.type_name == value.type_name

    def __hash__(self) -> int:
        return hash((type(self), self.type_name))

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            if self.error <= Errors.create_final:
                return self.error
            if (output := self.factory.group.domain.type_stuff.default_types.get(self.type_name, ...)) is ...:
                trace.exception(RuntimeError(f"Type {self.type_name} does not exist"))
                return self.narrow(Errors.create_final)
            self.type_result = output
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        return ((type,), self.error)

    def link_final(self, trace: Trace) -> tuple[type[T] | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            self.linked_final = True
            return self.type_result, None, self.error
        return ..., None, self.narrow(Errors.link_final)
