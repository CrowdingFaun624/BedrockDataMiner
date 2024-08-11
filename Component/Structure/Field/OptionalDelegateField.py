from typing import TYPE_CHECKING, Any, Callable, Union

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.FunctionChecker as FunctionChecker
import Structure.Delegate.DefaultBaseDelegate as DefaultBaseDelegate
import Structure.Delegate.DefaultDelegate as SU
import Structure.Delegate.Delegate as Delegate
import Structure.Delegate.VolumeDelegate as VolumeDelegate
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component
    import Structure.Structure as Structure
    import Structure.StructureBase as StructureBase

delegate_types:dict[str,type[Delegate.Delegate]] = {delegate_type.__name__: delegate_type for delegate_type in (SU.DefaultDelegate, DefaultBaseDelegate.DefaultBaseDelegate, VolumeDelegate.VolumeDelegate)}

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

    def create_delegate(self, structure:Union["Structure.Structure", "StructureBase.StructureBase", None], keys:dict[str,Any]|None=None) -> Delegate.Delegate|None:
        delegate_type = self.get_delegate_type()
        if delegate_type is None:
            return None
        if keys is None:
            keys = {}
        exception:Exception|None = None
        try:
            return delegate_type(structure, keys, **self.arguments)
        except Exception as e:
            print("Failed to create Delegate of %r!" % (structure,))
            exception = e
        if exception is not None:
            raise exception

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
            delegate_type = delegate_types.get(self.delegate_name)
            if delegate_type is None:
                raise Exceptions.UnrecognizedDelegateError(self.delegate_name, repr(source_component))
            self.delegate_type = delegate_type
        return [], []

    def check(self, source_component: "Component.Component") -> list[Exception]:
        exceptions = super().check(source_component)
        exceptions.extend(FunctionChecker.check(self.delegate_type.__init__, self.arguments, {"self", "structure", "keys"}, source_component))
        return exceptions
