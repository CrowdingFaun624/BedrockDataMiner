from types import EllipsisType
from typing import Hashable, Mapping, Sequence

from Component.Field.Errors import Errors
from Component.Field.Field import Field
from Component.Field.FieldFactory import FieldFactory
from Component.Group import ScriptFile
from Component.PropagatingVariables import PropagatingVariables
from Component.ReferenceResolver import (
    resolve_domain_reference,
    resolve_group_reference,
)
from Component.Scope import Scope
from Component.Scripts import Script
from Utilities.Trace import Trace


class ScriptField(Field[Script]):

    __slots__ = (
        "domain_name",
        "force_built_in",
        "group_path",
        "script",
        "script_name",
    )

    requires_variables = False

    def __init__(self, factory: FieldFactory, scope:Scope, error: Errors, domain_name:str|None, group_path:Sequence[str]|None, script_name:str|None, force_built_in:bool) -> None:
        super().__init__(factory, scope, error)
        self.domain_name = domain_name
        self.group_path = group_path
        self.script_name = script_name
        self.force_built_in = force_built_in
        self.script:Script

    def __eq__(self, value: object) -> bool:
        return isinstance(value, type(self)) and self.factory.group == value.factory.group and self.domain_name == value.domain_name and self.group_path == value.group_path \
        and self.script_name == value.script_name and self.force_built_in == value.force_built_in

    def __hash__(self) -> int:
        return hash((type(self), self.factory.group, self.domain_name, tuple(self.group_path) if self.group_path is not None else None, self.script_name, self.force_built_in))

    def create_field(self, memo: set[FieldFactory], trace: Trace) -> Errors:
        with trace.enter_field(self, ...):
            memo.add(self.factory)
            if super().create_field(memo, trace) <= Errors.create_field:
                return self.error
            scripts = self.factory.group.domain.scripts

            if   (self.group_path is     None) and (self.script_name is not None) and (self.domain_name is     None):
                if self.force_built_in:
                    script, new_error = self.get_script(self.script_name, scripts.built_in_scripts, scripts.built_in_multiple_scripts, trace)
                else:
                    script, new_error = self.get_script(self.script_name, scripts.name_scripts, scripts.name_multiple_scripts, trace)

            elif (self.group_path is     None) and (self.script_name is not None) and (self.domain_name is not None):
                domain, new_error = resolve_domain_reference(self.factory, self.domain_name, set(), trace)
                if self.narrow(new_error) <= Errors.create_field:
                    return self.error
                assert domain is not ...
                script, new_error = self.get_script((domain, self.script_name), scripts.domain_name_scripts, scripts.domain_name_multiple_scripts, trace)

            elif (self.group_path is not None) and (self.script_name is     None): # domain_name being None does not matter
                script_file, new_error = resolve_group_reference(self.factory, self.domain_name, self.group_path, set(), trace, ScriptFile)
                if self.narrow(new_error) <= Errors.create_field:
                    return self.error
                assert script_file is not ...
                script, new_error = self.get_script(script_file, scripts.group_scripts, scripts.group_multiple_scripts, trace)

            elif (self.group_path is not None) and (self.script_name is not None): # domain_name being None does not matter
                script_file, new_error = resolve_group_reference(self.factory, self.domain_name, self.group_path, set(), trace, ScriptFile)
                if self.narrow(new_error) <= Errors.create_field:
                    return self.error
                assert script_file is not ...
                script, new_error = self.get_script((script_file, self.script_name), scripts.group_name_scripts, scripts.group_name_multiple_scripts, trace)

            else:
                trace.exception(RuntimeError("Not enough information to select any Script!"))
                return self.narrow(Errors.create_field)

            if self.narrow(new_error) <= Errors.create_field:
                return self.error
            assert script is not ...
            self.script = script
            return self.error
        return self.narrow(Errors.create_field)

    def get_script[K:Hashable](self, key:K, scripts_map:Mapping[K, Script], duplicates_map:Mapping[K, Sequence[Script]], trace:Trace) -> tuple["Script|EllipsisType", Errors]:
        """
        Returns a Script from the information given.

        :param key: The key object from the reference.
        :param scripts_map: The `(key)_scripts` attribute from the `Scripts` object.
        :param duplicates_map: The `(key)_multiple_scripts` attribute from the `Scripts` object.
        """
        if (output := scripts_map.get(key)) is not None:
            return output, Errors.fine
        elif (duplicates := duplicates_map.get(key)) is not None:
            if len(duplicates) < 5:
                trace.exception(RuntimeError(f"Multiple Scripts have key {key}: {duplicates}"))
            else:
                trace.exception(RuntimeError(f"{len(duplicates)} Scripts have key {key}"))
            return ..., Errors.create_field
        else:
            trace.exception(RuntimeError(f"There are no scripts with key {key}"))
            return ..., Errors.create_field

    def get_final_type(self, trace: Trace) -> tuple[tuple[type, ...], Errors]:
        return ((Script,), self.error)

    def link_final(self, trace: Trace) -> tuple[Script | EllipsisType, PropagatingVariables | None, Errors]:
        with trace.enter_field(self, ...):
            if self.error <= Errors.link_final:
                return ..., None, self.error
            self.linked_final = True
            return self.script, None, self.error
        return ..., None, self.narrow(Errors.link_final)

    def destroy(self) -> None:
        if self.destroyed: return
        super().destroy()
        del self.script
