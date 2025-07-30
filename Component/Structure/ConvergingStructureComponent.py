from typing import Sequence

from Component.ComponentTyping import ConvergingStructureTypedDict
from Component.Field.ComponentField import ComponentField, OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.StructureComponent import (
    STRUCTURE_COMPONENT_PATTERN,
    StructureComponent,
)
from Structure.ConvergingStructure import ConvergingStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class ConvergingStructureComponent(StructureComponent[ConvergingStructure]):

    class_name = "Converging"
    structure_type = ConvergingStructure
    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("end_structure", True, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("structure", True, (str, dict)),
        TypedDictKeyTypeVerifier("tags", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("this_types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("within_structure_depth", True, int)
    ))

    def initialize_fields(self, data: ConvergingStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.within_structure_depth = data["within_structure_depth"]

        self.end_structure_field = OptionalComponentField(data.get("end_structure"), STRUCTURE_COMPONENT_PATTERN, ("end_structure",))
        self.structure_field = ComponentField(data.get("structure"), STRUCTURE_COMPONENT_PATTERN, ("structure",))
        self.tags_field = TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.this_types_field = TypeListField(data["this_types"], ("this_types",)).add_to_set(self.my_type).verify_with(self.structure_field)

        fields.extend((self.end_structure_field, self.structure_field, self.tags_field, self.this_types_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        self.final.link_converging_structure(
            end_structure=self.end_structure_field.map(lambda subcomponent: subcomponent.final),
            structure=self.structure_field.subcomponent.final,
            tags=self.tags_field.finals,
            this_types=self.this_types_field.types,
            within_structure_depth=self.within_structure_depth,
        )
