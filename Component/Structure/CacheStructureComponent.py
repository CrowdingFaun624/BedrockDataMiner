from typing import Sequence

from Component.ComponentTyping import CacheStructureTypedDict
from Component.Field.Field import Field
from Component.Structure.BranchlessStructureComponent import (
    BranchlessStructureComponent,
)
from Component.Structure.Field.DelegateField import OptionalDelegateField
from Structure.StructureTypes.CacheStructure import CacheStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class CacheStructureComponent(BranchlessStructureComponent[CacheStructure]):

    __slots__ = (
        "delegate_field",
        "removal_threshold",
    )

    class_name = "Cache"
    structure_type = CacheStructure
    type_verifier = BranchlessStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("removal_threshold", False, int),
        TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
    ))

    def initialize_fields(self, data: CacheStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))
        self.removal_threshold = data.get("removal_threshold", 2)

        self.delegate_field = OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))

        fields.append(self.delegate_field)
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_cache_structure(
            cache_versions_for_delegates=self.variable_bools["children_has_version_domains"],
            delegate=self.delegate_field.create_delegate(self.final, trace),
            removal_threshold=self.removal_threshold,
        )
