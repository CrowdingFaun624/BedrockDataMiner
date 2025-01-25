from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FunctionField as FunctionField
import Component.Structure.Field.DelegateField as DelegateField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.StringStructure as StringStructure
import Utilities.TypeVerifier as TypeVerifier


class StringComponent(StructureComponent.StructureComponent[StringStructure.StringStructure]):

    class_name = "String"
    my_capabilities = Capabilities.Capabilities(is_primitive=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("similarity_function", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    )

    __slots__ = (
        "delegate_field",
        "max_similarity_ancestor_depth",
        "normalizer_field",
        "pre_normalized_types_field",
        "similarity_function_field",
        "tags_field",
        "types_field",
    )

    def initialize_fields(self, data: ComponentTyping.StringTypedDict) -> Sequence[Field.Field]:
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", 6) # it's common to have a set of dicts with a significant string like [{"name": "bob"}, {"name": "alice"}]

        self.delegate_field = DelegateField.OptionalDelegateField(data.get("delegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.tags_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.types_field = TypeListField.TypeListField(data.get("types", "str"), ("types",)).must_be(self.domain.type_stuff.string_types).add_to_set(self.my_type)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",))
        self.similarity_function_field = FunctionField.OptionalFunctionField(data.get("similarity_function", None), ("similarity_function",))
        return (self.delegate_field, self.normalizer_field, self.tags_field, self.types_field, self.pre_normalized_types_field, self.similarity_function_field)

    def create_final(self) -> StringStructure.StringStructure:
        return StringStructure.StringStructure(
            name=self.name,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=self.types_field.types,
            normalizer=tuple(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.types_field.types,
            tags=self.tags_field.finals,
            similarity_function=self.similarity_function_field.function,
            children_tags={tag.final for tag in self.children_tags},
        )
        return exceptions
