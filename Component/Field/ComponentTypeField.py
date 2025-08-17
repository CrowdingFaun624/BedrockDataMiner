from types import EllipsisType

from Component.ComponentObject import ComponentObject
from Component.ComponentTypes import component_types_dict
from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace


class ComponentTypeField(Field[type[ComponentObject]]):

    __slots__ = (
        "component_type",
        "type_name",
    )

    requires_variables = False

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, type_name:str) -> None:
        super().__init__(factory, scope, error)
        self.type_name = type_name
        self.component_type: type[ComponentObject]

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and self.type_name == value.type_name # does not depend on Scope.

    def __hash__(self) -> int:
        return hash((type(self), self.type_name))

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            super().create_final(trace)
            component_type = component_types_dict.get(self.type_name, ...)
            if component_type is ...:
                trace.exception(RuntimeError(f"Unrecognized Component type {self.type_name}"))
                self.narrow(Errors.create_final)
                return self.error
            self.component_type = component_type.object_type
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        return ((type,), self.error)

    def link_final(self, trace: Trace) -> tuple[type[ComponentObject] | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            self.linked_final = True
            return self.component_type, None, self.error
        return ..., None, self.narrow(Errors.link_final)
