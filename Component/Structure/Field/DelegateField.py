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
import Utilities.TypeVerifier as TypeVerifier


class OptionalDelegateField(Field.Field):

    __slots__ = (
        "arguments",
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

    def create_delegate(self, structure:"Structure.Structure|StructureBase.StructureBase|None", keys:dict[str,Any]|None=None, exceptions:list[Exception]|None=None) -> Delegate.Delegate|None:
        '''
        Returns a Delegate or None.
        :structure: The parent Structure of this Delegate.
        :keys: Arguments for the Delegate's keys.
        :exceptions: List to add Exceptions with creating the Delegate to, instead of raising them.
        '''
        if (exceptions_missing := exceptions is None):
            exceptions = []
        delegate_type = self.delegate_type
        if delegate_type is None:
            return None
        if delegate_type.type_verifier is not None:
            exceptions.extend(delegate_type.type_verifier.verify(self.arguments, TypeVerifier.StackTrace([(structure, TypeVerifier.TraceItemType.OTHER)])))
        if keys is not None and delegate_type.key_type_verifier is not None:
            for key, key_arguments in keys.items():
                exceptions.extend(delegate_type.key_type_verifier.verify(key_arguments, TypeVerifier.StackTrace([(structure, TypeVerifier.TraceItemType.OTHER), (key, TypeVerifier.TraceItemType.KEY)])))
        if keys is None:
            keys = {}
        if not isinstance(structure, delegate_type.applies_to):
            exceptions.append(Exceptions.InapplicableDelegateError(delegate_type, structure, delegate_type.applies_to))
        if len(exceptions) == 0:
            try:
                delegate = delegate_type(structure, keys, **self.arguments)
            except Exception as e:
                print(f"Failed to create Delegate of {structure}!")
                exceptions.append(e)
                delegate = None
        else:
            delegate = None
        if exceptions_missing and len(exceptions) > 0:
            raise exceptions[0]
        return delegate

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[Sequence["Component.Component"],Sequence["Component.Component"]]:
        if self.delegate_name is None:
            self.delegate_type = None
        else:
            delegate_type = functions.delegate_classes.get(self.delegate_name, source_component, self.error_path)
            self.delegate_type = delegate_type
        return (), ()
