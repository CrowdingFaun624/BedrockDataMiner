from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.SetStructure as SetStructure
import Utilities.TypeVerifier as TypeVerifier


class SetComponent(StructureComponent.StructureComponent[SetStructure.SetStructure]):

    class_name = "Set"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("min_similarity_threshold", False, float),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("sort", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    )

    __slots__ = (
        "delegate_field",
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "min_similarity_threshold",
        "my_type",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "sort",
        "subcomponent_field",
        "tags_field",
        "this_type_field",
        "types_field",
    )

    def initialize_fields(self, data: ComponentTyping.SetTypedDict) -> Sequence[Field.Field]:
        self.sort = data.get("sort", False)
        self.min_similarity_threshold = data.get("min_similarity_threshold", SetStructure.MIN_SIMILARITY_THRESHOLD)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 6)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponent_field = OptionalComponentField.OptionalComponentField(data["subcomponent"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("subcomponent",))
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.types_field = TypeListField.TypeListField(data["types"], ("types",)).verify_with(self.subcomponent_field).conditional_must_be(self.sort, self.domain.type_stuff.sortable_types, fail_message="(due to being sorted)")
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("post_normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",))
        self.tags_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "list"), ("this_type",)).must_be(self.domain.type_stuff.iterable_types).contained_by(self.types_field)
        return (self.subcomponent_field, self.delegate_field, self.types_field, self.normalizer_field, self.this_type_field, self.tags_field, self.pre_normalized_types_field, self.post_normalizer_field)

    def create_final(self) -> SetStructure.SetStructure:
        return SetStructure.SetStructure(
            name=self.name,
            sort=self.sort,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            min_similarity_threshold=self.min_similarity_threshold,
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            structure=self.subcomponent_field.get_final(lambda subcomponent: subcomponent.final),
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=self.types_field.types,
            normalizer=tuple(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=tuple(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.this_type_field.types,
            tags=self.tags_field.finals,
            children_tags={tag.final for tag in self.children_tags},
        )
        self.my_type = set(self.this_type_field.types)
        return exceptions
