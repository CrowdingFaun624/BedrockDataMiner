from typing import Sequence

from Component.ComponentTyping import BranchlessStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
)
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.BranchlessStructure import BranchlessStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class BranchlessStructureComponent[a: BranchlessStructure](PassthroughStructureComponent[a]):

    __slots__ = (
        "structure_field",
        "this_types_field",
    )

    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("structure", True, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("this_types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: BranchlessStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.structure_field = OptionalComponentField(data["structure"], STRUCTURE_COMPONENT_PATTERN, ("structure",))
        self.this_types_field = TypeListField(data["this_types"], ("this_types",)).add_to_set(self.my_type).verify_with(self.structure_field)

        fields.extend((self.structure_field, self.this_types_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_branchless_structure(
            this_types=self.this_types_field.types,
            structure=self.structure_field.map(lambda subcomponent: subcomponent.final),
        )
