from itertools import chain
from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.Field.TypeField as TypeField
import Component.Structure.PassthroughStructureComponent as PassthroughStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.Structure as Structure
import Structure.StructureTypes.UnionStructure as UnionStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class UnionStructureComponent(PassthroughStructureComponent.PassthroughStructureComponent[UnionStructure.UnionStructure]):

    __slots__ = (
        "subcomponents_field",
    )

    class_name = "Union"
    structure_type = UnionStructure.UnionStructure
    type_verifier = PassthroughStructureComponent.PassthroughStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("substructures", True, TypeVerifier.DictTypeVerifier(dict, str, (str, dict, type(None)))),
    ))

    def initialize_fields(self, data: ComponentTyping.UnionStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.subcomponents_field = [
            (
                (subcomponent_field := ComponentField.OptionalComponentField(subcomponent_str, StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("substructures", type_str))),
                TypeField.TypeField(type_str, ("substructures", type_str)).verify_with(subcomponent_field).add_to_set(self.my_type).make_default(self.pre_normalized_types_field),
            )
            for index, (type_str, subcomponent_str) in enumerate(data["substructures"].items())
        ]
        fields.extend(chain.from_iterable(self.subcomponents_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            substructures:dict[type,Structure.Structure|None] = {}
            for (subcomponent_field, type_field) in self.subcomponents_field:
                substructures.update((valid_type, subcomponent_field.map(lambda subcomponent: subcomponent.final)) for valid_type in type_field.types)
            self.final.link_union_structure(
                substructures=substructures,
            )
