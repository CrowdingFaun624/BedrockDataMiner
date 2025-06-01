from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.PassthroughStructureComponent as PassthroughStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.BranchlessStructure as BranchlessStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class BranchlessStructureComponent[a: BranchlessStructure.BranchlessStructure](PassthroughStructureComponent.PassthroughStructureComponent[a]):

    __slots__ = (
        "structure_field",
        "this_types_field",
    )

    type_verifier = PassthroughStructureComponent.PassthroughStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("structure", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: ComponentTyping.BranchlessStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.structure_field = ComponentField.OptionalComponentField(data["structure"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("structure",))
        self.this_types_field = TypeListField.TypeListField(data["this_types"], ("this_types",)).add_to_set(self.my_type).make_default(self.pre_normalized_types_field).verify_with(self.structure_field)

        fields.extend((self.structure_field, self.this_types_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_branchless_structure(
                this_types=self.this_types_field.types,
                structure=self.structure_field.map(lambda subcomponent: subcomponent.final),
            )
