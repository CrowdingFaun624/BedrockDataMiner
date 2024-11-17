import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.SetStructure as SetStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class SetComponent(StructureComponent.StructureComponent[SetStructure.SetStructure]):

    class_name_article = "a Set"
    class_name = "Set"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("min_similarity_threshold", "a float", False, float),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("sort", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent, or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.SetTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.sort = data.get("sort", False)
        self.min_similarity_threshold = data.get("min_similarity_threshold", SetStructure.MIN_SIMILARITY_THRESHOLD)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 4)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(data["subcomponent"], ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), ["delegate"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.tags_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "list"), ["this_type"])
        self.types_field.verify_with(self.subcomponent_field)
        if self.sort:
            self.types_field.must_be(StructureComponent.SORTABLE_TYPES, fail_message="(due to being sorted)")
        self.tags_field.add_to_tag_set(self.children_tags)
        self.this_type_field.must_be(StructureComponent.ITERABLE_TYPES)
        self.this_type_field.contained_by(self.types_field)
        self.fields.extend([self.subcomponent_field, self.delegate_field, self.types_field, self.normalizer_field, self.this_type_field, self.tags_field, self.pre_normalized_types_field, self.post_normalizer_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = SetStructure.SetStructure(
            name=self.name,
            sort=self.sort,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            min_similarity_threshold=self.min_similarity_threshold,
            children_has_normalizer=self.children_has_normalizer,
            children_has_garbage_collection=self.children_has_garbage_collection,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            delegate=self.delegate_field.create_delegate(self.get_final(), exceptions=exceptions),
            types=self.types_field.get_types(),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else self.this_type_field.get_types(),
            tags=self.tags_field.get_finals(),
            children_tags={tag.get_final() for tag in self.children_tags},
        )
        self.my_type = set(self.this_type_field.get_types())
        return exceptions
