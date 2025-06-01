from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.BranchlessStructureComponent as BranchlessStructureComponent
import Component.Structure.Field.DelegateField as DelegateField
import Structure.StructureBase as StructureBase
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

STRUCTURE_BASE_PATTERN:Pattern.Pattern["StructureBaseComponent"] = Pattern.Pattern("is_base")

class StructureBaseComponent(BranchlessStructureComponent.BranchlessStructureComponent[StructureBase.StructureBase]):

    __slots__ = (
        "default_delegate_field",
        "delegate_field",
    )

    class_name = "StructureBase"
    structure_type = StructureBase.StructureBase
    my_capabilities = Capabilities.Capabilities(is_base=True, is_structure=True)
    type_verifier = BranchlessStructureComponent.BranchlessStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("default_delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("default_delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
    ))

    def initialize_fields(self, data: ComponentTyping.StructureBaseTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.default_delegate_field = DelegateField.OptionalDelegateField(data.get("default_delegate", "PrimitiveDelegate"), data.get("default_delegate_arguments", {}), self.domain, ("default_delegate",))
        self.delegate_field = DelegateField.OptionalDelegateField(data.get("delegate", "DefaultBaseDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))

        fields.extend((self.default_delegate_field, self.delegate_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_structure_base(
                default_delegate=self.default_delegate_field.create_delegate(None, trace),
                delegate=self.delegate_field.create_delegate(self.final, trace),
                domain=self.domain,
            )

    def finalize(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            self.final.finalize()
