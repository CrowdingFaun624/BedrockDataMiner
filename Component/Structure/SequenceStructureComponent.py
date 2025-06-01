from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.IterableStructureComponent as IterableStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.StructureTypes.SequenceStructure as SequenceStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class SequenceStructureComponent(IterableStructureComponent.IterableStructureComponent[SequenceStructure.SequenceStructure]):

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
    structure_type = SequenceStructure.SequenceStructure
    type_verifier = IterableStructureComponent.IterableStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("addition_cost", False, float),
        TypeVerifier.TypedDictKeyTypeVerifier("deletion_cost", False, float),
        TypeVerifier.TypedDictKeyTypeVerifier("key_structure", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_weight", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_square_length", False, int),
        TypeVerifier.TypedDictKeyTypeVerifier("substitution_cost", False, float),
        TypeVerifier.TypedDictKeyTypeVerifier("value_structure", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("value_types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("value_weight", False, int),
    ))

    def initialize_fields(self, data: ComponentTyping.SequenceStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.addition_cost = data.get("addition_cost", 1.0)
        self.deletion_cost = data.get("deletion_cost", 1.0)
        self.key_weight = data.get("key_weight", None) # None means do some logic to determine the best weight.
        self.max_square_length = data.get("max_square_length", 10000)
        self.substitution_cost = data.get("substitution_cost", 4.0)
        self.value_weight = data.get("value_weight", self.structure_type.VALUE_WEIGHT)

        self.key_structure_field = ComponentField.OptionalComponentField(data.get("key_structure", None), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("key_structure",))
        self.key_types_field.verify_with(self.key_structure_field)
        self.value_structure_field = ComponentField.OptionalComponentField(data["value_structure"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("value_structure",))
        self.value_types_field = TypeListField.TypeListField(data["value_types"], ("value_Types",)).verify_with(self.value_structure_field)

        fields.extend((self.key_structure_field, self.value_structure_field, self.value_types_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
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
