from itertools import chain
from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.FilterComponent as FilterComponent
import Component.Structure.PassthroughStructureComponent as PassthroughStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.StructureTypes.ConditionStructure as ConditionStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class ConditionStructureComponent(PassthroughStructureComponent.PassthroughStructureComponent[ConditionStructure.ConditionStructure]):

    __slots__ = (
        "substructures_field",
    )

    class_name = "Condition"
    structure_type = ConditionStructure.ConditionStructure
    type_verifier = PassthroughStructureComponent.PassthroughStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("substructures", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("filter", True, (str, dict, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("structure", False, (str, dict, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        ), list)),
    ))

    def initialize_fields(self, data: ComponentTyping.ConditionStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.substructures_field = [
            (
                ComponentField.OptionalComponentField(item["filter"], FilterComponent.FILTER_PATTERN, ("substructures", str(index), "filter")),
                (structure_field := ComponentField.OptionalComponentField(item.get("structure"), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("substructures", str(index), "structure"))),
                TypeListField.TypeListField(item["types"], ("substructures", str(index), "types")).add_to_set(self.my_type).make_default(self.pre_normalized_types_field).verify_with(structure_field),
            )
            for index, item in enumerate(data["substructures"])
        ]
        fields.extend(chain.from_iterable(self.substructures_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_condition_structure(
                substructures=[(
                    type_field.types,
                    filter_field.map(lambda subcomponent: subcomponent.final),
                    structure_field.map(lambda subcomponent: subcomponent.final)
                ) for filter_field, structure_field, type_field in self.substructures_field],
            )
