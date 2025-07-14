from typing import Sequence

from Component.ComponentTyping import DictStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.MappingStructureComponent import MappingStructureComponent
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.StructureTypes.DictStructure import DictStructure
from Utilities.Exceptions import ZeroWeightError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


def data_verify_function(data:DictStructureTypedDict) -> tuple[bool, str]:
    if data.get("key_weight", 1) == 0 and data.get("value_weight", 1) == 0:
        return False, "key weight and value weight cannot both be 0"
    return True, ""

class DictStructureComponent(MappingStructureComponent[DictStructure]):

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
    structure_type = DictStructure
    default_this_types_name = "dict"
    type_verifier = MappingStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allow_key_moves", False, bool),
        TypedDictKeyTypeVerifier("allow_same_key_optimization", False, (bool, type(None))),
        TypedDictKeyTypeVerifier("key_structure", False, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("key_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypedDictKeyTypeVerifier("value_structure", True, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("value_types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("value_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        function=data_verify_function,
    ))

    def initialize_fields(self, data: DictStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.allow_key_moves = data.get("allow_key_moves", True)
        self.allow_same_key_optimization = data.get("allow_same_key_optimization", None)
        self.key_weight = data.get("key_weight", self.structure_type.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", self.structure_type.VALUE_WEIGHT)

        self.key_structure_field = OptionalComponentField(data.get("key_structure", None), STRUCTURE_COMPONENT_PATTERN, ("key_structure",))
        self.key_types_field.verify_with(self.key_structure_field)
        self.value_structure_field = OptionalComponentField(data["value_structure"], STRUCTURE_COMPONENT_PATTERN, ("value_structure",))
        self.value_types_field = TypeListField(data["value_types"], ("value_types",)).verify_with(self.value_structure_field)
        fields.extend((self.key_structure_field, self.value_structure_field, self.value_types_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_dict_structure(
            allow_key_moves=self.allow_key_moves,
            allow_same_key_optimization=self.allow_same_key_optimization if self.allow_same_key_optimization is not None else self.value_weight == 0 or not self.allow_key_moves or all(issubclass(this_type, dict) for this_type in self.this_types_field.types),
            key_structure=self.key_structure_field.map(lambda subcomponent: subcomponent.final),
            key_weight=self.key_weight,
            value_structure=self.value_structure_field.map(lambda subcomponent: subcomponent.final),
            value_types=self.value_types_field.types,
            value_weight=self.value_weight,
        )

    def check(self, trace: Trace) -> None:
        if self.key_weight + self.value_weight == 0:
            trace.exception(ZeroWeightError("key_weight", "value_weight"))
