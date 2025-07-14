from typing import Sequence

from Component.ComponentTyping import PassthroughStructureTypedDict
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.NormalizerComponent import (
    NORMALIZER_PATTERN,
    NormalizerComponent,
)
from Component.Structure.StructureComponent import StructureComponent
from Structure.AbstractPassthroughStructure import AbstractPassthroughStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class PassthroughStructureComponent[a: AbstractPassthroughStructure](StructureComponent[a]):

    __slots__ = (
        "normalizers_field",
        "post_normalizers_field",
        "pre_normalized_types_field",
        "tags_field",
    )

    type_verifier = StructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("normalizers", False, UnionTypeVerifier(str, dict, ListTypeVerifier((str, dict), list))),
        TypedDictKeyTypeVerifier("post_normalizers", False, UnionTypeVerifier(str, dict, ListTypeVerifier((str, dict), list))),
        TypedDictKeyTypeVerifier("pre_normalized_types", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("tags", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: PassthroughStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.normalizers_field = ComponentListField(data.get("normalizers", ()), NORMALIZER_PATTERN, ("normalizers",), assume_type=NormalizerComponent.class_name)
        self.post_normalizers_field = ComponentListField(data.get("post_normalizers", ()), NORMALIZER_PATTERN, ("post_normalizers",), assume_type=NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",)) # should declare default in subclasses.
        self.tags_field = TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)

        fields.extend((self.normalizers_field, self.post_normalizers_field, self.pre_normalized_types_field, self.tags_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_passthrough_structure(
            normalizers=tuple(self.normalizers_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizers=tuple(self.post_normalizers_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types,
            tags=self.tags_field.finals,
        )
