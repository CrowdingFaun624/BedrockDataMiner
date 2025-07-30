from typing import Sequence

from Component.ComponentTyping import PassthroughStructureTypedDict
from Component.Field.Field import Field
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.StructureComponent import StructureComponent
from Structure.PassthroughStructure import PassthroughStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class PassthroughStructureComponent[a: PassthroughStructure](StructureComponent[a]):

    __slots__ = (
        "tags_field",
    )

    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("tags", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: PassthroughStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.tags_field = TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)

        fields.append(self.tags_field)
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_passthrough_structure(
            tags=self.tags_field.finals,
        )
