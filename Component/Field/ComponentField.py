from types import EllipsisType
from typing import Any, Sequence, cast

from Component.Component import Component
from Component.ComponentObject import ComponentObject
from Component.ComponentTypes import component_types_dict
from Component.Field.ContainerField import ContainerField
from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory, FieldSlot
from Component.Field.Variable import Variable
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace


class ComponentField[R: ComponentObject](ContainerField[R]):

    __slots__ = (
        "component",
        "component_type",
        "component_type_name",
        "field_slots",
        "propagating_variables",
    )

    allow_abstract = True

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, component_type_name:str, fields: Sequence[tuple[str,FieldFactory[Field|Variable]]]) -> None:
        field_slots = [(key, FieldSlot(field)) for key, field in fields]
        super().__init__(factory, scope, error, field_slots)
        self.field_slots:Sequence[tuple[str,FieldSlot]] = field_slots
        self.component_type_name = component_type_name
        self.component_type:type[Component[R]]
        self.component:Component[R]
        self.propagating_variables:PropagatingVariables

    def __eq__(self, value: object) -> bool:
        # using optional_scope here works because the only place where __eq__ or __hash__ can be called
        # is during Scope-y stuff. In that case, all Fields compared will have the same Scope anyways.
        return isinstance(value, type(self)) and self.scope == value.scope and self.field_slots == value.field_slots

    def __hash__(self) -> int:
        return hash((type(self), self.scope, tuple(self.field_slots)))

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            if super().create_final(trace) <= Errors.create_final:
                return self.error
            del self.field_slots
            component_type = cast("type[Component[R]]|None", component_types_dict.get(self.component_type_name))
            if component_type is None:
                trace.exception(RuntimeError(f"Unrecognized Component type {self.component_type_name}"))
                self.narrow(Errors.create_final)
                return self.error
            for field in self.subscope.local_fields.values():
                self.narrow(field.create_final(trace))
                # We do not break or return if the Errors can be narrowed.
                # The creation of sub-Fields do not affect the creation of the
                # Component.
            self.component_type = component_type
            # using self.index here does not uphold scopiness correctly.
            # significant index will be removed soon.
            if self.scope.name is not None:
                full_name, name = self.scope.name
            else:
                full_name, name = self.factory.full_name, self.factory.name
            component = self.component_type(full_name, name, self.factory.group, self.factory.index, self.factory.is_inline)
            component.create_final()
            component.propagating_booleans, component.propagating_sets = propagating_booleans, propagating_sets = component.get_propagating_variables()
            self.propagating_variables = PropagatingVariables(propagating_booleans, propagating_sets, [], suggestible=False)
            self.component = component
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        with trace.enter_field(self, ...):
            return ((self.component_type,), self.error)
        return (), self.narrow(Errors.create_field)

    def link_final_early(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables|None|EllipsisType, Errors]:
        if self.error <= Errors.link_final:
            return ..., None, self.error
        return self.component.final, self.propagating_variables, self.error

    def link_final(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.linked_final:
                return self.component.final, self.propagating_variables, self.error
            self.linked_final = True
            fields:dict[str,Any] = {}
            for key, field in self.subscope.local_fields.items():
                value, value_propagating_variables, new_error = field.link_final(trace)
                if self.narrow(new_error) <= Errors.link_final:
                    continue
                assert value is not ...
                self.propagating_variables.add(value_propagating_variables)
                fields[key] = value
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.component.check(fields, trace):
                self.narrow(Errors.link_final)
                return ..., None, self.error
            self.component.link_final(fields)
            return self.component.final, self.propagating_variables, self.error
        return ..., None, self.narrow(Errors.link_final)

    def finalize(self, trace: Trace) -> Errors:
        if self.finalized: return self.error
        with trace.enter_field(self, ...):
            if super().finalize(trace) <= Errors.finalize:
                return self.error
            for subfield in self.subscope.local_fields.values():
                self.narrow(subfield.finalize(trace))
            if self.error <= Errors.finalize:
                return self.error
            if self.component.post_check(self.component.fields, trace):
                self.narrow(Errors.finalize)
                return self.error
            propagating_booleans, propagating_sets = self.propagating_variables.merge(set())
            if self.component.finalize(propagating_booleans, propagating_sets, trace):
                self.narrow(Errors.finalize)
                return self.error
            return self.error
        return self.narrow(Errors.finalize)

    def destroy(self) -> None:
        if self.destroyed: return
        super().destroy()
        if self.created_final:
            self.component.destroy()
            del self.component
            self.propagating_variables.destroy()
            del self.propagating_variables
