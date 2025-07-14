from itertools import chain
from typing import Sequence

from Component.ComponentTyping import SwitchStructureTypedDict
from Component.Field.ComponentField import ComponentField, OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.NormalizerComponent import (
    NORMALIZER_PATTERN,
    NormalizerComponent,
)
from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
)
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.StructureTypes.SwitchStructure import SwitchStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class SwitchStructureComponent(PassthroughStructureComponent[SwitchStructure]):

    __slots__ = (
        "subcomponents_field",
        "switch_function_field",
    )

    class_name = "Switch"
    structure_type = SwitchStructure
    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("switch_function", True, (str, dict)),
        TypedDictKeyTypeVerifier("substructures", True, DictTypeVerifier(dict, str, TypedDictTypeVerifier(
            TypedDictKeyTypeVerifier("structure", False, (str, dict, type(None))),
            TypedDictKeyTypeVerifier("types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        ))),
    ))

    def initialize_fields(self, data: SwitchStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.switch_function_field = ComponentField(data["switch_function"], NORMALIZER_PATTERN, ("switch_function",), assume_type=NormalizerComponent.class_name)
        self.subcomponents_field = {
            key: (
                (structure_field := OptionalComponentField(subdata.get("structure"), STRUCTURE_COMPONENT_PATTERN, ("substructures", key, "structure"))),
                TypeListField(subdata["types"], ("substructures", key, "types")).make_default(self.pre_normalized_types_field).verify_with(structure_field).add_to_set(self.my_type),
            )
            for key, subdata in data["substructures"].items()
        }

        fields.append(self.switch_function_field)
        fields.extend(chain.from_iterable(self.subcomponents_field.values()))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_switch_structure(
            switch_function=self.switch_function_field.subcomponent.final,
            structures={key_field.key: key_field.structure_field.map(lambda component: component.final) for key_field in self.subcomponents_field},
            tags={key.key: tags for key in self.subcomponents_field if len(tags := set(key.tags_field.map(lambda subcomponent: subcomponent.final))) != 0},
            types={key_field.key: key_field.types_field.types for key_field in self.subcomponents_field},
        )
