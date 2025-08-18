from types import EllipsisType
from typing import TYPE_CHECKING, Final

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.VariableReferenceField import VariableReferenceField
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Field.CTypeField import CTypeField
    from Component.Field.FieldFactory import FieldFactory


class Variable[R](Field[R]):
    """
    A type of custom Field that gets moved around through Scopes a bunch.
    """

    __slots__ = (
        "propagating_variables",
        "referenced_field",
        "result",
        "types",
        "value_exists",
        "variable_value",
    )

    def __init__(self, factory: "FieldFactory", scope:Scope, error: Errors, types:"FieldFactory[CTypeField]|None", value:"FieldFactory[Field[R]]|None") -> None:
        super().__init__(factory, scope, error)
        self.types:Final = types
        self.variable_value:Final = value
        self.referenced_field:Field[R] # may be modified
        self.result: R
        self.value_exists:bool = value is not None
        self.propagating_variables: PropagatingVariables|None

    def __eq__(self, value: object) -> bool:
        if self.variable_value is None:
            # if the Variable has no value, it is a declaration Variable.
            # these Variables never use their own Scope.
            return isinstance(value, type(self)) and self.variable_value == value.variable_value # still compare just in case the other's isn't None.
        return isinstance(value, type(self)) and self.optional_scope == value.optional_scope and self.variable_value == value.variable_value

    def __hash__(self) -> int:
        if self.variable_value is None:
            return hash((type(self), self.variable_value)) # hash a tuple of different length so that it won't be confused with an unequal Variable with no Scope
        return hash((type(self), self.optional_scope, self.variable_value))

    @property
    def is_declaration(self) -> bool:
        """
        :returns: True if the types exist, and False if they do not.
        """
        return self.types is not None

    @property
    def is_defined(self) -> bool:
        """
        :returns: True if the Variable has an initial value, not one assigned later.
        """
        return self.variable_value is not None

    def assign_value(self, new_value:"Field[R]") -> None:
        """
        Modifies this Variable to have a new value. Don't screw up the
        scopiness! Will freak out if it already has a value.

        :param new_value: The value to write to this Variable.
        """
        if self.types is None: raise RuntimeError("Hey you're only supposed to give new values to declared Variables")
        if new_value is self:
            return
        self.referenced_field = new_value
        self.value_exists = True

    def create_field(self, memo: set["FieldFactory"], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if super().create_field(memo, trace) <= Errors.create_field:
                return self.error
            if self.variable_value is None: # may happen when an abstract Field is used, and does not necessarily mean an error will occur.
                return self.error
            referenced_field, new_error = self.variable_value.create_field(self.scope, memo, trace)
            if self.narrow(new_error) <= Errors.create_field:
                return self.error
            assert referenced_field is not ...
            while isinstance(referenced_field, VariableReferenceField):
                if self.narrow(referenced_field.error) <= Errors.create_field:
                    return self.error
                other_variable = referenced_field.variable
                if self.narrow(other_variable.error) <= Errors.create_field:
                    return self.error
                referenced_field = other_variable.referenced_field
            if referenced_field is self:
                trace.exception(RuntimeError("Variable cannot reference itself"))
                return self.narrow(Errors.create_field)
            self.referenced_field = referenced_field
            return self.error
        return self.narrow(Errors.create_field)

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            if self.error <= Errors.create_final:
                return self.error
            if not self.value_exists:
                trace.exception(RuntimeError(f"{self} is not defined. Consider making this Field abstract"))
                return self.narrow(Errors.create_final)
            self.narrow(self.referenced_field.create_final(trace))
            return self.error
        return self.narrow(Errors.create_final)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        with trace.enter_field(self, ...):
            output, new_error = self.referenced_field.get_final_type(trace)
            return output, self.narrow(new_error)
        return (), self.narrow(Errors.create_final)

    def link_final(self, trace: Trace) -> tuple[R | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            if self.linked_final: return self.result, self.propagating_variables, self.error
            result, propagating_variables, new_error = self.referenced_field.link_final(trace)
            if self.narrow(new_error) <= Errors.link_final:
                return ..., None, self.error
            assert result is not ...
            self.result = result
            self.propagating_variables = propagating_variables
            self.linked_final = True
            return result, propagating_variables, self.error
        return ..., None, self.narrow(Errors.link_final)
