from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Structure.BranchlessStructureComponent as BranchlessStructureComponent
import Component.Structure.Field.DelegateField as DelegateField
import Structure.StructureTypes.CacheStructure as CacheStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class CacheStructureComponent(BranchlessStructureComponent.BranchlessStructureComponent[CacheStructure.CacheStructure]):

    __slots__ = (
        "delegate_field",
        "removal_threshold",
    )

    class_name = "Cache"
    structure_type = CacheStructure.CacheStructure
    type_verifier = BranchlessStructureComponent.BranchlessStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("removal_threshold", False, int),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
    ))

    def initialize_fields(self, data: ComponentTyping.CacheStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))
        self.removal_threshold = data.get("removal_threshold", 10)

        self.delegate_field = DelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))

        fields.append(self.delegate_field)
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_cache_structure(
                delegate=self.delegate_field.create_delegate(self.final, trace),
                removal_threshold=self.removal_threshold,
            )
