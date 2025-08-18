from types import EllipsisType
from typing import Any, Final, Sequence

from Component.Field.ContainerField import ContainerField
from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory, FieldSlot
from Component.Field.Variable import Variable
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace


class ListField[V](ContainerField[Sequence[V]]):

    __slots__ = (
        "field_slots",
        "fields",
        "propagating_variables",
        "result",
        "sequence",
    )

    allow_abstract = True

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, sequence: Sequence[tuple[str,FieldFactory]]) -> None:
        field_slots = [(key_string, FieldSlot(field)) for key_string, field in sequence]
        super().__init__(factory, scope, error, field_slots)
        self.sequence:Final = sequence
        self.field_slots:Sequence[tuple[str,FieldSlot]] = field_slots
        self.fields:Sequence[Field]
        self.result: list[V]
        self.propagating_variables: PropagatingVariables

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and ( len(self.field_slots) == 0 and len(value.field_slots) == 0 or\
            self.optional_scope == value.optional_scope) and self.field_slots == value.field_slots

    def __hash__(self) -> int:
        return hash((type(self), (self.optional_scope if len(self.field_slots) > 0 else None), tuple(self.field_slots)))

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if super().create_field(memo, trace) <= Errors.create_field:
                return self.error
            self.fields = [field.field for _, field in self.field_slots if not isinstance(field.field, Variable)]
            return self.error
        return self.narrow(Errors.create_field)

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            if super().create_final(trace) <= Errors.create_final:
                return self.error
            del self.field_slots
            self.result = []
            self.propagating_variables = PropagatingVariables.new_empty(suggestible=True)
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        return ((list,), self.error)

    def link_final_early(self, trace: Trace) -> tuple[Sequence[V] | EllipsisType, PropagatingVariables|None|EllipsisType, Errors]:
        if self.error <= Errors.link_final:
            return ..., None, self.error
        return self.result, self.propagating_variables, self.error

    def link_final(self, trace: Trace) -> tuple[Sequence[V] | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.linked_final:
                return self.result, self.propagating_variables, self.error
            # we set it to True before linking sub-Fields because that way,
            # this ListField can reference itself.
            self.linked_final = True
            for item_field in self.fields:
                item, item_propagating_variables, new_error = item_field.link_final(trace)
                if self.narrow(new_error) <= Errors.link_final:
                    continue
                assert item is not ...
                if self.narrow(self.validate_item(item, trace)) <= Errors.link_final:
                    continue
                self.propagating_variables.add(item_propagating_variables)
                self.result.append(item)
            return self.result, self.propagating_variables, self.error
        return ..., None, self.narrow(Errors.link_final)

    def validate_item(self, item:Any, trace:Trace) -> Errors:
        """
        Used to validate that the items of this ListField are correct.
        """
        return Errors.fine

    def finalize(self, trace: Trace) -> Errors:
        if self.finalized: return self.error
        with trace.enter_field(self, ...):
            super().finalize(trace)
            if self.error <= Errors.finalize:
                return self.error
            for subfield in self.fields:
                self.narrow(subfield.finalize(trace))
            return self.error
        return self.narrow(Errors.finalize)

    def destroy(self) -> None:
        if self.destroyed: return
        super().destroy()
        del self.sequence # type: ignore
        for field in self.fields:
            field.destroy()
        del self.fields
        if self.created_final:
            del self.result
            self.propagating_variables.destroy()
            del self.propagating_variables
