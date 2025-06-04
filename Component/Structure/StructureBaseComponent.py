from typing import Sequence

from Component.Capabilities import Capabilities
from Component.ComponentTyping import StructureBaseTypedDict
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Component.Structure.BranchlessStructureComponent import (
    BranchlessStructureComponent,
)
from Component.Structure.Field.DelegateField import OptionalDelegateField
from Structure.StructureBase import StructureBase
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

STRUCTURE_BASE_PATTERN:Pattern["StructureBaseComponent"] = Pattern("is_base")

class StructureBaseComponent(BranchlessStructureComponent[StructureBase]):

    __slots__ = (
        "default_delegate_field",
        "delegate_field",
    )

    class_name = "StructureBase"
    structure_type = StructureBase
    my_capabilities = Capabilities(is_base=True, is_structure=True)
    type_verifier = BranchlessStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("default_delegate", False, (str, type(None))),
        TypedDictKeyTypeVerifier("default_delegate_arguments", False, dict),
        TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
    ))

    def initialize_fields(self, data: StructureBaseTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.default_delegate_field = OptionalDelegateField(data.get("default_delegate", "PrimitiveDelegate"), data.get("default_delegate_arguments", {}), self.domain, ("default_delegate",))
        self.delegate_field = OptionalDelegateField(data.get("delegate", "DefaultBaseDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))

        fields.extend((self.default_delegate_field, self.delegate_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_structure_base(
                default_delegate=self.default_delegate_field.create_delegate(None, trace),
                delegate=self.delegate_field.create_delegate(self.final, trace),
                domain=self.domain,
            )

    def finalize(self, trace: Trace) -> None:
        with trace.enter(self, self.name, ...):
            self.final.finalize()
