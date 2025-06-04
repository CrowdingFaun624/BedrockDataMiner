from typing import Any, Sequence

import Domain.Domain as Domain
from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.Field import Field
from Component.ScriptImporter import ScriptSetSetSet
from Structure.Delegate.Delegate import Delegate
from Structure.Structure import Structure
from Utilities.Exceptions import InapplicableDelegateError
from Utilities.Trace import Trace


class OptionalDelegateField(Field):

    __slots__ = (
        "arguments",
        "delegate",
        "delegate_name",
        "delegate_type",
        "domain",
    )

    def __init__(self, delegate_name:str|None, arguments:dict[str,Any], domain:"Domain.Domain", path: tuple[str,...]) -> None:
        super().__init__(path)
        self.delegate_name = delegate_name
        self.arguments = arguments
        self.domain = domain

        self.delegate_type:type[Delegate]|None
        self.delegate:Delegate|None = None

    def create_delegate(self, structure:"Structure|None", trace:Trace, keys:dict[str,Any]|None=None) -> Delegate|None:
        '''
        Returns a Delegate or None.
        :structure: The parent Structure of this Delegate.
        :keys: Arguments for the Delegate's keys.
        :exceptions: List to add Exceptions with creating the Delegate to, instead of raising them.
        '''
        with trace.enter_keys(self.trace_path, (self.delegate_name, self.arguments)):
            delegate_type = self.delegate_type
            if delegate_type is None:
                return None
            if delegate_type.type_verifier is not None:
                if delegate_type.type_verifier.verify(self.arguments, trace):
                    return None

            if keys is not None and delegate_type.key_type_verifier is not None:
                for key, key_arguments in keys.items():
                    with trace.enter_key(key, key_arguments):
                        if delegate_type.key_type_verifier.verify(key_arguments, trace):
                            return None

            if keys is None:
                keys = {}
            if not ((structure is not None and structure.any_delegate_works) or isinstance(structure, delegate_type.applies_to)):
                trace.exception(InapplicableDelegateError(delegate_type, structure, delegate_type.applies_to))
                return None
            self.delegate = delegate_type(structure, keys, **self.arguments)
            return self.delegate
        return None

    def set_field(
        self,
        source_component:"Component",
        components:dict[str,"Component"],
        global_components:dict[str,dict[str,dict[str,"Component"]]],
        functions:ScriptSetSetSet,
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["Component"],Sequence["Component"]]:
        with trace.enter_keys(self.trace_path, (self.delegate_name, self.arguments)):
            if self.delegate_name is None:
                self.delegate_type = None
            else:
                delegate_type = functions.delegate_classes.get(self.delegate_name, source_component)
                self.delegate_type = delegate_type
            if self.delegate_type is not None and self.delegate_type.uses_versions:
                source_component.variable_bools["children_has_version_domains"] = True
            return (), ()
        return (), ()

    def finalize(self, trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, (self.delegate_name, self.arguments)):
            if self.delegate is not None:
                self.delegate.finalize(self.domain, trace)
