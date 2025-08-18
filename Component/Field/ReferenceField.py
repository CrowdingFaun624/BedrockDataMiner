from types import EllipsisType
from typing import Sequence

from Component.Field.ContainerField import ContainerField
from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory, FieldSlot
from Component.Field.Variable import Variable
from Component.PropagatingVariables import PropagatingVariables
from Component.ReferenceResolver import resolve_field_reference
from Component.Scope import Scope
from Utilities.Trace import Trace


class ReferenceField[R](ContainerField[R]):
    """
    References Fields and overrides their Fields and Variables with its own.

    :param domain: The name of the Domain in the reference.
    :param group_path: The path to the Group of the referenced Field.
    :param component_name: The name of the referenced Field in its Group.
    :param fields: Sub-Fields to override the referenced Field's with.
    :param variables: Sub-Variables to override the referenced Variable's with.
    :param is_forgetful: If True, Variables from above will not be used to evaluate the referenced Field.
    :param is_absolute: If True, the Field's original Group will be used instead of the Scope's current Group.
    """

    __slots__ = (
        "component_name",
        "domain",
        "field_slots",
        "group_path",
        "is_forgetful",
        "propagating_variables",
        "referenced_field",
        "result",
        "variable_slots",
    )

    allow_abstract = True

    def __init__(
        self,
        factory: FieldFactory,
        scope:Scope,
        error: Errors,
        domain:str|None,
        group_path:Sequence[str],
        component_name:str,
        fields:Sequence[tuple[str,FieldFactory]],
        is_forgetful:bool,
    ) -> None:
        field_slots:list[tuple[str,FieldSlot]] = []
        variable_slots:list[tuple[str,FieldSlot[Variable]]] = []
        all_field_slots:list[tuple[str,FieldSlot]] = []
        for field_name, field in fields:
            field_slot = FieldSlot(field)
            if issubclass(field.field_type, Variable):
                variable_slots.append((field_name, field_slot))
            else:
                field_slots.append((field_name, field_slot))
            all_field_slots.append((field_name, field_slot))

        super().__init__(factory, scope, error, all_field_slots)
        self.domain = domain
        self.group_path = group_path
        self.component_name = component_name
        self.field_slots:Sequence[tuple[str,FieldSlot]] = field_slots
        self.variable_slots:Sequence[tuple[str,FieldSlot[Variable]]] = variable_slots
        self.is_forgetful = is_forgetful
        self.referenced_field:Field[R]
        self.result: R
        self.propagating_variables: PropagatingVariables|None

    def __eq__(self, value: object) -> bool:
        # When there are no Field slots or Variable slots, the Scope does not matter
        return isinstance(value, type(self)) and (self.is_forgetful and len(self.variable_slots) == 0 and len(value.variable_slots) == 0 and len(self.field_slots) == 0 and len(value.field_slots) == 0 \
        or self.optional_scope == value.optional_scope) and self.domain == value.domain and self.group_path == value.group_path and self.component_name == value.component_name \
        and self.is_forgetful is value.is_forgetful and self.field_slots == value.field_slots and self.variable_slots == value.variable_slots

    def __hash__(self) -> int:
        return hash((type(self), self.optional_scope if not self.is_forgetful or len(self.field_slots) > 0 or len(self.variable_slots) > 0 else None, self.domain, tuple(self.group_path),
                     self.component_name, self.is_forgetful, tuple(self.field_slots), tuple(self.variable_slots)))

    def get_subscope(self) -> Scope:
        """
        The Scope for referencing the referenced Field.
        """
        if self.is_forgetful:
            return self.scope.override(
                None,
                {key: variable.field for key, variable in self.variable_slots},
                {key: field.field for key, field in self.field_slots},
                forget_above_variables=True,
            )
        else:
            return self.scope.override(
                self.factory.name if self.scope.name is None else self.scope.name,
                {key: variable.field for key, variable in self.variable_slots},
                {key: field.field for key, field in self.field_slots},
                forget_above_variables=True,
            )

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if super().create_field(memo, trace) <= Errors.create_field:
                return self.error
            referenced_field_factory, new_error = resolve_field_reference(self.factory, self.domain, self.group_path, self.component_name, trace)
            if self.narrow(new_error) <= Errors.create_field:
                return self.error
            assert referenced_field_factory is not ...
            referenced_field, new_error = referenced_field_factory.create_field(self.get_subscope(), memo, trace)
            if self.narrow(new_error) <= Errors.create_field:
                return self.error
            assert referenced_field is not ...
            self.referenced_field = referenced_field
            return self.error
        return self.narrow(Errors.create_field)

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            super().create_final(trace)
            if self.error <= Errors.create_final:
                return self.error
            del self.field_slots
            del self.variable_slots
            self.narrow(self.referenced_field.create_final(trace))
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        with trace.enter_field(self, ...):
            output, new_error = self.referenced_field.get_final_type(trace)
            return output, self.narrow(new_error)
        return (), self.narrow(Errors.create_final)

    def link_final_early(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables|None|EllipsisType, Errors]:
        if self.error <= Errors.link_final:
            return ..., None, self.error
        return self.referenced_field.link_final_early(trace)

    def link_final(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.linked_final:
                return self.result, self.propagating_variables, self.error
            self.linked_final = True
            result, propagating_variables, new_error = self.referenced_field.link_final_early(trace)
            if self.narrow(new_error) <= Errors.link_final:
                return ..., None, self.error
            if result is not ...:
                self.result = result
            if propagating_variables is not ...:
                self.propagating_variables = propagating_variables
            result, propagating_variables, new_error = self.referenced_field.link_final(trace)
            if self.narrow(new_error) <= Errors.link_final:
                return ..., None, self.error
            assert result is not ...
            self.result = result
            self.propagating_variables = propagating_variables
            return result, propagating_variables, self.error
        return ..., None, self.narrow(Errors.link_final)

    def finalize(self, trace: Trace) -> Errors:
        if self.finalized: return self.error
        with trace.enter_field(self, ...):
            if super().finalize(trace) <= Errors.finalize:
                return self.error
            for subfield in self.subfields:
                self.narrow(subfield.finalize(trace))
            if self.error <= Errors.finalize:
                return self.error
            self.narrow(self.referenced_field.finalize(trace))
            return self.error
        return self.narrow(Errors.finalize)

    def destroy(self) -> None:
        if self.destroyed: return
        super().destroy()
        self.referenced_field.destroy()
        del self.referenced_field
        if self.linked_final:
            del self.result
            if self.propagating_variables is not None:
                self.propagating_variables.destroy()
            del self.propagating_variables
