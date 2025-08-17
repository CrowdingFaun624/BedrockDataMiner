from types import EllipsisType

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace


class ConcatenationField[R](Field[R]):

    __slots__ = (
        "field_factory1",
        "field_factory2",
        "field1",
        "field2",
        "propagating_variables",
        "result",
    )

    allow_abstract = True

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, factory1:FieldFactory[Field[R]], factory2:FieldFactory[Field[R]]) -> None:
        super().__init__(factory, scope, error)
        self.field_factory1 = factory1
        self.field_factory2 = factory2
        self.field1: Field[R]
        self.field2: Field[R]
        self.propagating_variables: PropagatingVariables
        self.result: R

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and self.field_factory1 == value.field_factory1 and self.field_factory2 == value.field_factory2 and self.scope == value.scope

    def __hash__(self) -> int:
        return hash((type(self), self.field_factory1, self.field_factory2, self.scope))

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if super().create_field(memo, trace) <= Errors.create_field:
                return self.error
            # we copy the memo because there could be a situation where we do reference + reference.
            field1, new_error = self.field_factory1.create_field(self.scope, memo.copy(), trace)
            self.narrow(new_error)
            field2, new_error = self.field_factory2.create_field(self.scope, memo, trace)
            if self.narrow(new_error) <= Errors.create_field:
                return self.error
            assert field1 is not ... and field2 is not ...
            self.field1, self.field2 = field1, field2
            return self.error
        return self.narrow(Errors.create_field)

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            if super().create_final(trace) <= Errors.create_final:
                return self.error
            self.propagating_variables = PropagatingVariables.new_empty(suggestible=True)
            self.field1.create_final(trace)
            self.field2.create_final(trace)
            # It doesn't actually need to create its final now, even if it's a list or dict.
            # This is because this Field cannot reference itself.
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        with trace.enter_field(self, ...):
            type1, new_error = self.field1.get_final_type(trace)
            self.narrow(new_error)
            type2, new_error = self.field2.get_final_type(trace)
            if self.narrow(new_error) <= Errors.create_final:
                return (), self.error
            # unions are currently not supported because it is unclear if they will be of the same type.
            if len(type1) != 1 or len(type2) != 1:
                trace.exception(RuntimeError("Unions are not acceptable in ConcatenationField"))
                return (), self.narrow(Errors.create_final)
            type1, = type1 # unpack single-item tuple
            type2, = type2
            if   issubclass(type1, int) and issubclass(type2, int): return ((int,), self.error)
            elif issubclass(type1, (int, float)) and issubclass(type2, (int, float)): return ((float,), self.error)
            elif issubclass(type1, str) and issubclass(type2, str): return ((str,), self.error)
            elif issubclass(type1, list) and issubclass(type2, list): return ((list,), self.error)
            elif issubclass(type1, dict) and issubclass(type2, dict): return ((dict,), self.error)
            else:
                trace.exception(RuntimeError(f"Concatenation is not supported between {type1.__name__} and {type2.__name__}"))
                return (), self.narrow(Errors.create_final)
        return (), self.narrow(Errors.create_final)

    def link_final(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.linked_final:
                return self.result, self.propagating_variables, self.error
            final1, propagating_variables1, new_error = self.field1.link_final(trace)
            self.narrow(new_error)
            final2, propagating_variables2, new_error = self.field2.link_final(trace)
            if self.narrow(new_error) <= Errors.link_final:
                return ..., None, self.error
            assert final1 is not ... and final2 is not ...
            self.propagating_variables.add(propagating_variables1, propagating_variables2)
            try:
                if isinstance(final1, dict):
                    result = self.result = final1 | final2 # type: ignore
                else:
                    result = self.result = final1 + final2 # type: ignore we'll deal with that when we add type safety
            except TypeError as e:
                e.add_note(f"{final1} and {final2}")
                raise
            return result, self.propagating_variables, self.error
        return ..., None, self.narrow(Errors.link_final)

    def finalize(self, trace: Trace) -> Errors:
        if self.finalized: return self.error
        with trace.enter_field(self, ...):
            if super().finalize(trace) <= Errors.finalize:
                return self.error
            self.field1.finalize(trace)
            self.field2.finalize(trace)
            return self.error
        return self.narrow(Errors.finalize)
