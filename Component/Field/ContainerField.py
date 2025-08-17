from typing import Sequence

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory, FieldSlot
from Component.Field.Variable import Variable
from Component.Scope import Scope
from Utilities.Trace import Trace


class ContainerField[R](Field[R]):
    '''
    Field that contains other Fields.

    :param subfields: Fields and Variables which this Field contains. Also has a string based on its key to append to the sub-Field's name.
    '''

    __slots__ = (
        "subfield_factories",
        "subfields",
        "subscope",
    )

    allow_abstract = True

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, subfields:Sequence[tuple[str,FieldSlot[Field|Variable]]]) -> None:
        super().__init__(factory, scope, error)
        self.subfield_factories = subfields
        if len(self.subfield_factories) > 0:
            self.narrows(subfield.field_factory.error for _, subfield in self.subfield_factories)
        self.subfields:Sequence[Field]
        self.subscope:Scope # The Scope that contains all of the overriding Fields and Variables.

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            if self.error <= Errors.create_field:
                return self.error
            memo.add(self.factory)
            subfields:list[Field] = []
            override_variables:dict[str,Variable] = {}
            override_fields:dict[str,Field] = {}
            scope = self.scope
            for field_name, subfield_factory in self.subfield_factories:
                subfield, new_error = subfield_factory.create_field(scope.sub(), trace)
                self.narrow(new_error)
                if new_error <= Errors.create_field:
                    # if sub-Field is a Variable and it failed, then any Fields
                    # after it could fail, too.
                    break
                assert subfield is not ...
                subfields.append(subfield)
                if isinstance(subfield, Variable):
                    override_variables[field_name] = subfield
                else:
                    override_fields[field_name] = subfield
                scope = self.scope.override(override_variables, override_fields)
            self.subfields = subfields
            self.subscope = scope

            return self.error
        return self.narrow(Errors.create_field)

    def create_final(self, trace: Trace) -> Errors:
        if self.created_final: return self.error
        with trace.enter_field(self, ...):
            super().create_final(trace)
            if self.error <= Errors.create_final:
                return self.error
            for subfield in self.subfields:
                self.narrow(subfield.create_final(trace))
            return self.error
        return self.narrow(Errors.create_final)

    # link_final is the responsibility of subclasses

    # finalize is also the responsibility of subclasses because sometimes a
    # Field overwrites another and the overwritten Field will never have
    # link_final called on it, so finalize cannot be called on it either.
