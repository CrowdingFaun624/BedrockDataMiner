from types import EllipsisType

import Domain.Domain as Domain
from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory
from Component.PropagatingVariables import PropagatingVariables
from Component.ReferenceResolver import resolve_domain_reference
from Component.Scope import Scope
from Utilities.Trace import Trace


class DomainField(Field["Domain.Domain"]):

    __slots__ = (
        "domain",
        "domain_name",
    )

    requires_variables = False

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, domain_name:str) -> None:
        super().__init__(factory, scope, error)
        self.domain_name = domain_name
        self.domain:"Domain.Domain"

    def __eq__(self, value: object) -> bool:
        # Scope does matter because of aliases
        return isinstance(value, type(self)) and self.factory.group.domain == value.factory.group.domain and self.domain_name == value.domain_name

    def __hash__(self) -> int:
        return hash((type(self), self.factory.group.domain, self.domain_name))

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if self.error <= Errors.create_field:
                return self.error
            domain, new_error = resolve_domain_reference(self.factory, self.domain_name, memo, trace, ignore_alias=self.factory)
            if self.narrow(new_error) <= Errors.create_field:
                return self.error
            assert domain is not ...
            self.domain = domain
            return self.error
        return self.narrow(Errors.create_field)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        return ((Domain.Domain,), self.error)

    def link_final(self, trace: Trace) -> tuple["Domain.Domain | EllipsisType", PropagatingVariables|None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            self.linked_final = True
            return self.domain, None, self.error
        return ..., None, self.narrow(Errors.link_final)
