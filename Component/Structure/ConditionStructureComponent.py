from itertools import chain
from typing import Sequence

from Component.ComponentTyping import ConditionStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.FilterComponent import FILTER_PATTERN
from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
)
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.StructureTypes.ConditionStructure import ConditionStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class ConditionStructureComponent(PassthroughStructureComponent[ConditionStructure]):

    __slots__ = (
        "substructures_field",
    )

    class_name = "Condition"
    structure_type = ConditionStructure
    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("substructures", True, ListTypeVerifier(TypedDictTypeVerifier(
            TypedDictKeyTypeVerifier("filter", True, (str, dict, type(None))),
            TypedDictKeyTypeVerifier("structure", False, (str, dict, type(None))),
            TypedDictKeyTypeVerifier("types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        ), list)),
    ))

    def initialize_fields(self, data: ConditionStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.substructures_field = [
            (
                OptionalComponentField(item["filter"], FILTER_PATTERN, ("substructures", str(index), "filter")),
                (structure_field := OptionalComponentField(item.get("structure"), STRUCTURE_COMPONENT_PATTERN, ("substructures", str(index), "structure"))),
                TypeListField(item["types"], ("substructures", str(index), "types")).add_to_set(self.my_type).make_default(self.pre_normalized_types_field).verify_with(structure_field),
            )
            for index, item in enumerate(data["substructures"])
        ]
        fields.extend(chain.from_iterable(self.substructures_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_condition_structure(
            substructures=[(
                type_field.types,
                filter_field.map(lambda subcomponent: subcomponent.final),
                structure_field.map(lambda subcomponent: subcomponent.final)
            ) for filter_field, structure_field, type_field in self.substructures_field],
        )
