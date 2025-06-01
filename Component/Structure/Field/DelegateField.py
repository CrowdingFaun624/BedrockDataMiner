from typing import Any, Sequence

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Domain.Domain as Domain
import Structure.Delegate.Delegate as Delegate
import Structure.Structure as Structure
import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class OptionalDelegateField(Field.Field):

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

        self.delegate_type:type[Delegate.Delegate]|None
        self.delegate:Delegate.Delegate|None = None

    def create_delegate(self, structure:"Structure.Structure|StructureBase.StructureBase|None", trace:Trace.Trace, keys:dict[str,Any]|None=None) -> Delegate.Delegate|None:
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
                trace.exception(Exceptions.InapplicableDelegateError(delegate_type, structure, delegate_type.applies_to))
                return None
            self.delegate = delegate_type(structure, keys, **self.arguments)
            return self.delegate
        return None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
        trace:Trace.Trace,
    ) -> tuple[Sequence["Component.Component"],Sequence["Component.Component"]]:
        with trace.enter_keys(self.trace_path, (self.delegate_name, self.arguments)):
            if self.delegate_name is None:
                self.delegate_type = None
            else:
                delegate_type = functions.delegate_classes.get(self.delegate_name, source_component)
                self.delegate_type = delegate_type
            return (), ()
        return (), ()

    def finalize(self, trace:Trace.Trace) -> None:
        with trace.enter_keys(self.trace_path, (self.delegate_name, self.arguments)):
            if self.delegate is not None:
                self.delegate.finalize(self.domain, trace)
