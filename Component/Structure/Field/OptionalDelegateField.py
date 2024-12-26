from typing import TYPE_CHECKING, Any, Callable, Union

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.FunctionChecker as FunctionChecker
import Component.ScriptImporter as ScriptImporter
import Structure.Delegate.DefaultBaseDelegate as DefaultBaseDelegate
import Structure.Delegate.DefaultDelegate as DefaultDelegate
import Structure.Delegate.Delegate as Delegate
import Structure.Delegate.LongStringDelegate as LongStringDelegate
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.Component as Component
    import Structure.Structure as Structure
    import Structure.StructureBase as StructureBase

BUILT_IN_DELEGATE_CLASSES:dict[str,type[Delegate.Delegate]] = {delegate_type.__name__: delegate_type for delegate_type in [
    Delegate.Delegate,
    DefaultDelegate.DefaultDelegate,
    DefaultBaseDelegate.DefaultBaseDelegate,
    LongStringDelegate.LongStringDelegate,
]}

DELEGATE_CLASSES = ScriptImporter.import_scripted_types("delegates", BUILT_IN_DELEGATE_CLASSES, Delegate.Delegate)

class OptionalDelegateField(Field.Field):

    def __init__(self, delegate_name:str|None, arguments:dict[str,Any], path: list[str | int]) -> None:
        super().__init__(path)
        self.delegate_name = delegate_name
        self.arguments = arguments

        self.delegate_type:type[Delegate.Delegate]|None = None
        self.has_set_delegate = False

    def get_delegate_type(self) -> type[Delegate.Delegate]|None:
        if not self.has_set_delegate:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_delegate_type, self)
        return self.delegate_type

    def create_delegate(self, structure:Union["Structure.Structure", "StructureBase.StructureBase", None], keys:dict[str,Any]|None=None, exceptions:list[Exception]|None=None) -> Delegate.Delegate|None:
        '''
        Returns a Delegate or None.
        :structure: The parent Structure of this Delegate.
        :keys: Arguments for the Delegate's keys.
        :exceptions: List to add Exceptions with creating the Delegate to, instead of raising them.
        '''
        if (exceptions_missing := exceptions is None):
            exceptions = []
        delegate_type = self.get_delegate_type()
        if delegate_type is None:
            return None
        if delegate_type.type_verifier is not None:
            exceptions.extend(delegate_type.type_verifier.verify(self.arguments, TypeVerifier.Trace([(structure, TypeVerifier.TraceItemType.OTHER)])))
        if keys is not None and delegate_type.key_type_verifier is not None:
            for key, key_arguments in keys.items():
                exceptions.extend(delegate_type.key_type_verifier.verify(key_arguments, TypeVerifier.Trace([(structure, TypeVerifier.TraceItemType.OTHER), (key, TypeVerifier.TraceItemType.KEY)])))
        if keys is None:
            keys = {}
        if not isinstance(structure, delegate_type.applies_to):
            exceptions.append(Exceptions.InapplicableDelegateError(delegate_type, structure, delegate_type.applies_to))
        if len(exceptions) == 0:
            try:
                delegate = delegate_type(structure, keys, **self.arguments)
            except Exception as e:
                print("Failed to create Delegate of %r!" % (structure,))
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
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        self.has_set_delegate = True
        if self.delegate_name is None:
            self.delegate_type = None
        else:
            delegate_type = DELEGATE_CLASSES.get(self.delegate_name, message="(referenced by %r)" % (source_component,))
            self.delegate_type = delegate_type
        return [], []

    def check(self, source_component: "Component.Component") -> list[Exception]:
        exceptions = super().check(source_component)
        exceptions.extend(FunctionChecker.check(self.delegate_type.__init__, self.arguments, {"self", "structure", "keys"}, source_component))
        return exceptions
