from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.AbstractPassthroughStructure as AbstractPassthroughStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class PassthroughStructureComponent[a: AbstractPassthroughStructure.AbstractPassthroughStructure](StructureComponent.StructureComponent[a]):

    __slots__ = (
        "normalizers_field",
        "post_normalizers_field",
        "pre_normalized_types_field",
        "tags_field",
    )

    type_verifier = StructureComponent.StructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("normalizers", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizers", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    ))

    def initialize_fields(self, data: ComponentTyping.PassthroughStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.normalizers_field = ComponentListField.ComponentListField(data.get("normalizers", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizers",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizers_field = ComponentListField.ComponentListField(data.get("post_normalizers", ()), NormalizerComponent.NORMALIZER_PATTERN, ("post_normalizers",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",)) # should declare default in subclasses.
        self.tags_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)

        fields.extend((self.normalizers_field, self.post_normalizers_field, self.pre_normalized_types_field, self.tags_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_passthrough_structure(
                normalizers=tuple(self.normalizers_field.map(lambda subcomponent: subcomponent.final)),
                post_normalizers=tuple(self.post_normalizers_field.map(lambda subcomponent: subcomponent.final)),
                pre_normalized_types=self.pre_normalized_types_field.types,
                tags=self.tags_field.finals,
            )
