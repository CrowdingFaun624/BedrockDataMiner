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
import Structure.SequenceStructure as SequenceStructure
import Utilities.TypeVerifier as TypeVerifier


class SequenceComponent(StructureComponent.StructureComponent[SequenceStructure.SequenceStructure]):

    class_name = "Sequence"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("addition_cost", "a float or int", False, (float, int)),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("deletion_cost", "a float or int", False, (float, int)),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent, or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("substitution_cost", "a float or int", False, (float, int)),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    __slots__ = (
        "addition_cost",
        "delegate_field",
        "deletion_cost",
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "my_type",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "subcomponent_field",
        "substitution_cost",
        "tags_field",
        "this_type_field",
        "types_field",
    )

    def initialize_fields(self, data: ComponentTyping.SequenceTypedDict) -> list[Field.Field]:
        self.addition_cost = data.get("addition_cost", 1)
        self.deletion_cost = data.get("deletion_cost", 1)
        self.substitution_cost = data.get("substitution_cost", 4)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 4)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", 1) # really expensive

        self.subcomponent_field = OptionalComponentField.OptionalComponentField(data["subcomponent"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ["delegate"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"]).verify_with(self.subcomponent_field)
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", []), NormalizerComponent.NORMALIZER_PATTERN, ["normalizer"], assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", []), NormalizerComponent.NORMALIZER_PATTERN, ["post_normalizer"], assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.tags_field = TagListField.TagListField(data.get("tags", []), ["tags"]).add_to_tag_set(self.children_tags)
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "list"), ["this_type"]).must_be(self.domain.type_stuff.iterable_types).contained_by(self.types_field)
        return [self.subcomponent_field, self.delegate_field, self.types_field, self.normalizer_field, self.this_type_field, self.tags_field, self.pre_normalized_types_field, self.post_normalizer_field]

    def create_final(self) -> SequenceStructure.SequenceStructure:
        return SequenceStructure.SequenceStructure(
            name=self.name,
            addition_cost=self.addition_cost,
            deletion_cost=self.deletion_cost,
            substitution_cost=self.substitution_cost,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            structure=self.subcomponent_field.get_final(lambda subcomponent: subcomponent.final),
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=self.types_field.types,
            normalizer=list(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=list(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.this_type_field.types,
            tags=self.tags_field.finals,
            children_tags={tag.final for tag in self.children_tags},
        )
        self.my_type = set(self.this_type_field.types)
        return exceptions
