from types import EllipsisType
from typing import Any, Final, Hashable, Mapping, Sequence

from Component.Field.ContainerField import ContainerField
from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory, FieldSlot
from Component.Field.Variable import Variable
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace


def _get_subfield_slots(field_slots:Sequence[tuple[int,str,FieldSlot,FieldSlot]], variable_slots:Sequence[tuple[int,str,FieldSlot[Variable]]]) -> Sequence[tuple[str,FieldSlot]]:
    output:list[tuple[str,FieldSlot[Field]]]
    if len(variable_slots) == 0:
        output = []
        for _, key_string, key_field, value_field in field_slots:
            output.append((f"Key {key_string}", key_field))
            output.append((key_string, value_field))
    else:
        subfield_slots:list[tuple[int,str,FieldSlot[Any]]] = []
        for index, key_string, value_field in variable_slots: # do Variables first because they are usually above Fields, so less work for sorting.
            subfield_slots.append((index, key_string, value_field))
        for index, key_string, key_field, value_field in field_slots:
            subfield_slots.append((index, f"Key {key_string}", key_field))
            subfield_slots.append((index, key_string, value_field))
        subfield_slots.sort(key=lambda item: item[0])
        output = [(key_string, field) for _, key_string, field in subfield_slots]
    return output

class DictField[K:Hashable, V](ContainerField[Mapping[K, V]]):

    __slots__ = (
        "field_slots",
        "fields",
        "mapping",
        "propagating_variables",
        "result",
        "variable_slots",
    )

    allow_abstract = True


    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, mapping:Sequence[tuple[int, str, FieldFactory, FieldFactory]], variables:Sequence[tuple[int, str, FieldFactory[Variable]]]) -> None:
        field_slots = [(index, key_string, FieldSlot(key_field), FieldSlot(value_field)) for index, key_string, key_field, value_field in mapping]
        variable_slots = [(index, key_string, FieldSlot(value_field)) for index, key_string, value_field in variables]

        super().__init__(factory, scope, error, _get_subfield_slots(field_slots, variable_slots))
        self.mapping: Final = mapping
        self.field_slots:Sequence[tuple[int, str, FieldSlot[Field[K]],FieldSlot[Field[V]]]] = field_slots
        self.variable_slots:Sequence[tuple[int, str, FieldSlot[Variable]]] = variable_slots
        self.fields:Sequence[tuple[str,Field[K],Field[V]]]
        self.result: dict[K, V]
        self.propagating_variables:PropagatingVariables

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and (len(self.field_slots) == 0 and len(value.field_slots) == 0 and len(self.variable_slots) == 0 and len(value.variable_slots) == 0 or self.scope == value.scope) \
            and self.field_slots == value.field_slots

    def __hash__(self) -> int:
        return hash((type(self), (self.scope if len(self.field_slots) > 0 or len(self.variable_slots) > 0 else None), tuple(self.field_slots)))

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if super().create_field(memo, trace) <= Errors.create_field:
                return self.error
            self.fields = [(key_string, key_field.field, value_field.field) for _, key_string, key_field, value_field in self.field_slots]
            return self.error
        return self.narrow(Errors.create_field)

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            if super().create_final(trace) <= Errors.create_final:
                return self.error
            del self.field_slots
            del self.variable_slots
            for field in self.subscope.local_fields.values():
                self.narrow(field.create_final(trace))
                # don't return early if error occurs
            self.result = {}
            self.propagating_variables = PropagatingVariables.new_empty(suggestible=True)
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        return ((dict,), self.error)

    def link_final_early(self, trace: Trace) -> tuple[Mapping[K, V] | EllipsisType, PropagatingVariables|None|EllipsisType, Errors]:
        if self.error <= Errors.link_final:
            return ..., None, self.error
        return self.result, self.propagating_variables, self.error

    def link_final(self, trace: Trace) -> tuple[Mapping[K, V] | EllipsisType, PropagatingVariables|None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.linked_final:
                return self.result, self.propagating_variables, self.error
            # we set it to True before linking sub-Fields because that way,
            # this DictField can reference itself.
            self.linked_final = True

            for _, key_field, value_field in self.fields:
                key, key_propagating_variables, new_error = key_field.link_final(trace)
                self.narrow(new_error) # don't need to `continue` yet, since keys and values are unrelated.
                value, value_propagating_variables, new_error = value_field.link_final(trace)
                if self.narrow(new_error) <= Errors.link_final:
                    continue
                assert key is not ... and value is not ...
                self.propagating_variables.add(value_propagating_variables, key_propagating_variables)
                self.result[key] = value
            if self.error <= Errors.link_final:
                return ..., None, self.error
            return self.result, self.propagating_variables, self.error
        return ..., None, self.narrow(Errors.link_final)

    def finalize(self, trace: Trace) -> Errors:
        if self.finalized: return self.error
        with trace.enter_field(self, ...):
            super().finalize(trace)
            if self.error <= Errors.finalize:
                return self.error
            for _, key_field, value_field in self.fields:
                self.narrow(key_field.finalize(trace))
                self.narrow(value_field.finalize(trace))
            return self.error
        return self.narrow(Errors.finalize)

    def destroy(self) -> None:
        if self.destroyed: return
        super().destroy()
        del self.mapping # type: ignore
        for _, key, value in self.fields:
            key.destroy()
            value.destroy()
        del self.fields
        if self.created_final:
            del self.result
            self.propagating_variables.destroy()
            del self.propagating_variables
