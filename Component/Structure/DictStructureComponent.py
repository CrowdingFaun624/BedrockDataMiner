from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.MappingStructureComponent as MappingStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.StructureTypes.DictStructure as DictStructure
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


def data_verify_function(data:ComponentTyping.DictStructureTypedDict) -> tuple[bool, str]:
    if data.get("key_weight", 1) == 0 and data.get("value_weight", 1) == 0:
        return False, "key weight and value weight cannot both be 0"
    return True, ""

class DictStructureComponent(MappingStructureComponent.MappingStructureComponent[DictStructure.DictStructure]):

    __slots__ = (
        "allow_key_moves",
        "allow_same_key_optimization",
        "key_structure_field",
        "key_weight",
        "value_structure_field",
        "value_types_field",
        "value_weight",
    )

    class_name = "Dict"
    structure_type = DictStructure.DictStructure
    default_this_types_name = "dict"
    type_verifier = MappingStructureComponent.MappingStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("allow_key_moves", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("allow_same_key_optimization", False, (bool, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_structure", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypeVerifier.TypedDictKeyTypeVerifier("value_structure", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("value_types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("value_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        function=data_verify_function,
    ))

    def initialize_fields(self, data: ComponentTyping.DictStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.allow_key_moves = data.get("allow_key_moves", True)
        self.allow_same_key_optimization = data.get("allow_same_key_optimization", None)
        self.key_weight = data.get("key_weight", self.structure_type.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", self.structure_type.VALUE_WEIGHT)

        self.key_structure_field = ComponentField.OptionalComponentField(data.get("key_structure", None), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("key_structure",))
        self.key_types_field.verify_with(self.key_structure_field)
        self.value_structure_field = ComponentField.OptionalComponentField(data["value_structure"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("value_structure",))
        self.value_types_field = TypeListField.TypeListField(data["value_types"], ("value_types",)).verify_with(self.value_structure_field)
        fields.extend((self.key_structure_field, self.value_structure_field, self.value_types_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_dict_structure(
                allow_key_moves=self.allow_key_moves,
                allow_same_key_optimization=self.allow_same_key_optimization if self.allow_same_key_optimization is not None else self.value_weight == 0 or not self.allow_key_moves or all(issubclass(key_type, str) for key_type in self.key_types_field.types),
                key_structure=self.key_structure_field.map(lambda subcomponent: subcomponent.final),
                key_weight=self.key_weight,
                value_structure=self.value_structure_field.map(lambda subcomponent: subcomponent.final),
                value_types=self.value_types_field.types,
                value_weight=self.value_weight,
            )

    def check(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            if self.key_weight + self.value_weight == 0:
                raise Exceptions.ZeroWeightError("key_weight", "value_weight")
