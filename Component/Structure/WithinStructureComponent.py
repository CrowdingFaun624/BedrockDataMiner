from typing import Sequence

from Component.ComponentTyping import WithinStructureTypedDict
from Component.Field.ComponentField import ComponentField
from Component.Field.Field import Field
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.StructureComponent import (
    STRUCTURE_COMPONENT_PATTERN,
    StructureComponent,
)
from Structure.WithinStructure import WithinStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class WithinStructureComponent[a:WithinStructure](StructureComponent[a]):

    __slots__ = (
        "inner_types_field",
        "outer_types_field",
        "structure_field",
        "tags_field",
    )

    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("inner_types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("outer_types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("structure", True, (str, dict)), # non-optional; NoneType is not allowed
        TypedDictKeyTypeVerifier("tags", False, UnionTypeVerifier(str, ListTypeVerifier(str, list)))
    ))

    def initialize_fields(self, data: WithinStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.structure_field = ComponentField(data["structure"], STRUCTURE_COMPONENT_PATTERN, ("structure",))
        self.inner_types_field = TypeListField(data["inner_types"], ("inner_types",)).verify_with(self.structure_field)
        self.outer_types_field = TypeListField(data["outer_types"], ("outer_types",)).add_to_set(self.my_type)
        self.tags_field = TagListField(data.get("tags", []), ("tags",)).add_to_tag_set(self.children_tags)

        fields.extend((self.inner_types_field, self.outer_types_field, self.structure_field, self.tags_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_within_structure(
            inner_types=self.inner_types_field.types,
            outer_types=self.outer_types_field.types,
            structure=self.structure_field.subcomponent.final,
            tags=self.tags_field.finals,
        )
