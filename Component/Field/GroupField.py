from types import EllipsisType
from typing import Sequence

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory
from Component.Group import Group
from Component.PropagatingVariables import PropagatingVariables
from Component.ReferenceResolver import resolve_group_reference
from Component.Scope import Scope
from Utilities.Trace import Trace


class GroupField(Field[Group]):

    __slots__ = (
        "domain_name",
        "group",
        "group_path",
    )

    requires_variables = False

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, domain_name:str|None, group_path:Sequence[str]) -> None:
        super().__init__(factory, scope, error)
        self.domain_name = domain_name
        self.group_path = group_path
        self.group:Group

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and self.group == value.group and self.domain_name == value.domain_name and self.group_path == value.group_path

    def __hash__(self) -> int:
        return hash((type(self), self.group, self.domain_name, tuple(self.group_path)))

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if self.error <= Errors.create_field:
                return self.error
            group_file, new_error = resolve_group_reference(self.factory, self.domain_name, self.group_path, memo, trace, ignore_alias=self.factory) # errors are handled by this function
            if self.narrow(new_error) <= Errors.create_field:
                return self.error
            assert group_file is not ...
            self.group = group_file.group
            return self.error
        return self.narrow(Errors.create_field)

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        return ((Group,), self.error)

    def link_final(self, trace: Trace) -> tuple[Group | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            self.linked_final = True
            return self.group, None, self.error
        return ..., None, self.narrow(Errors.link_final)

    def destroy(self) -> None:
        if self.destroyed: return
        super().destroy()
        del self.group
