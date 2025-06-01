from itertools import chain
from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.PassthroughStructureComponent as PassthroughStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.StructureTypes.SwitchStructure as SwitchStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class SwitchStructureComponent(PassthroughStructureComponent.PassthroughStructureComponent[SwitchStructure.SwitchStructure]):

    __slots__ = (
        "subcomponents_field",
        "switch_function_field",
    )

    class_name = "Switch"
    structure_type = SwitchStructure.SwitchStructure
    type_verifier = PassthroughStructureComponent.PassthroughStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("switch_function", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("substructures", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("structure", False, (str, dict, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        ))),
    ))

    def initialize_fields(self, data: ComponentTyping.SwitchStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.switch_function_field = ComponentField.ComponentField(data["switch_function"], NormalizerComponent.NORMALIZER_PATTERN, ("switch_function",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.subcomponents_field = {
            key: (
                (structure_field := ComponentField.OptionalComponentField(subdata.get("structure"), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("substructures", key, "structure"))),
                TypeListField.TypeListField(subdata["types"], ("substructures", key, "types")).make_default(self.pre_normalized_types_field).verify_with(structure_field).add_to_set(self.my_type),
            )
            for key, subdata in data["substructures"].items()
        }

        fields.append(self.switch_function_field)
        fields.extend(chain.from_iterable(self.subcomponents_field.values()))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_switch_structure(
                switch_function=self.switch_function_field.subcomponent.final,
                switches={key: (structure_field.map(lambda subcomponent: subcomponent.final), type_field.types) for key, (structure_field, type_field) in self.subcomponents_field.items()},
            )
