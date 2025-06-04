from typing import Sequence

from Component.ComponentTyping import SequenceStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.IterableStructureComponent import IterableStructureComponent
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.StructureTypes.SequenceStructure import SequenceStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class SequenceStructureComponent(IterableStructureComponent[SequenceStructure]):

    __slots__ = (
        "addition_cost",
        "deletion_cost",
        "key_structure_field",
        "key_weight",
        "max_square_length",
        "substitution_cost",
        "value_structure_field",
        "value_types_field",
        "value_weight",
    )

    class_name = "Sequence"
    default_this_types_name = "list"
    default_key_types_name = "int"
    structure_type = SequenceStructure
    type_verifier = IterableStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("addition_cost", False, float),
        TypedDictKeyTypeVerifier("deletion_cost", False, float),
        TypedDictKeyTypeVerifier("key_structure", False, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("key_weight", False, (int, type(None))),
        TypedDictKeyTypeVerifier("max_square_length", False, int),
        TypedDictKeyTypeVerifier("substitution_cost", False, float),
        TypedDictKeyTypeVerifier("value_structure", True, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("value_types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("value_weight", False, int),
    ))

    def initialize_fields(self, data: SequenceStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.addition_cost = data.get("addition_cost", 1.0)
        self.deletion_cost = data.get("deletion_cost", 1.0)
        self.key_weight = data.get("key_weight", None) # None means do some logic to determine the best weight.
        self.max_square_length = data.get("max_square_length", 10000)
        self.substitution_cost = data.get("substitution_cost", 4.0)
        self.value_weight = data.get("value_weight", self.structure_type.VALUE_WEIGHT)

        self.key_structure_field = OptionalComponentField(data.get("key_structure", None), STRUCTURE_COMPONENT_PATTERN, ("key_structure",))
        self.key_types_field.verify_with(self.key_structure_field)
        self.value_structure_field = OptionalComponentField(data["value_structure"], STRUCTURE_COMPONENT_PATTERN, ("value_structure",))
        self.value_types_field = TypeListField(data["value_types"], ("value_Types",)).verify_with(self.value_structure_field)

        fields.extend((self.key_structure_field, self.value_structure_field, self.value_types_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_sequence_structure(
                addition_cost=self.addition_cost,
                deletion_cost=self.deletion_cost,
                key_structure=self.key_structure_field.map(lambda subcomponent: subcomponent.final),
                key_weight=self.key_weight if self.key_weight is not None else (0 if all(issubclass(key_type, int) for key_type in self.key_types_field.types) else self.structure_type.KEY_WEIGHT),
                max_square_length=self.max_square_length,
                substitution_cost=self.substitution_cost,
                value_structure=self.value_structure_field.map(lambda subcomponent: subcomponent.final),
                value_types=self.value_types_field.types,
                value_weight=self.value_weight,
            )
