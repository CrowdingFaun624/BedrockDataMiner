from itertools import chain
from typing import Sequence

from Component.ComponentTyping import UnionStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TypeField import TypeField
from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
)
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.Structure import Structure
from Structure.StructureTypes.UnionStructure import UnionStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class UnionStructureComponent(PassthroughStructureComponent[UnionStructure]):

    __slots__ = (
        "subcomponents_field",
    )

    class_name = "Union"
    structure_type = UnionStructure
    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("substructures", True, DictTypeVerifier(dict, str, (str, dict, type(None)))),
    ))

    def initialize_fields(self, data: UnionStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.subcomponents_field = [
            (
                (subcomponent_field := OptionalComponentField(subcomponent_str, STRUCTURE_COMPONENT_PATTERN, ("substructures", type_str))),
                TypeField(type_str, ("substructures", type_str)).verify_with(subcomponent_field).add_to_set(self.my_type),
            )
            for type_str, subcomponent_str in data["substructures"].items()
        ]
        fields.extend(chain.from_iterable(self.subcomponents_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        substructures:dict[type,Structure|None] = {}
        for (subcomponent_field, type_field) in self.subcomponents_field:
            substructures.update((valid_type, subcomponent_field.map(lambda subcomponent: subcomponent.final)) for valid_type in type_field.types)
        self.final.link_union_structure(
            substructures=substructures,
        )
