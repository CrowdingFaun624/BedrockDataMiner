import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.PrimitiveStructure as PrimitiveStructure
import Utilities.TypeVerifier as TypeVerifier


class PrimitiveComponent(StructureComponent.StructureComponent[PrimitiveStructure.PrimitiveStructure]):

    class_name = "Primitive"
    class_name_article = "a Primitive"
    my_capabilities = Capabilities.Capabilities(is_primitive=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, dict, or list", False, TypeVerifier.UnionTypeVerifier("a str, dict, list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or dict", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    __slots__ = (
        "delegate_field",
        "my_type",
        "normalizer_field",
        "pre_normalized_types_field",
        "tags_field",
        "types_field",
    )

    def initialize_fields(self, data: ComponentTyping.PrimitiveTypedDict) -> list[Field.Field]:
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ["delegate"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.tags_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.tags_field.add_to_tag_set(self.children_tags)
        return [self.delegate_field, self.normalizer_field, self.tags_field, self.types_field, self.pre_normalized_types_field]

    def create_final(self) -> PrimitiveStructure.PrimitiveStructure:
        return PrimitiveStructure.PrimitiveStructure(
            name=self.name,
            children_has_normalizer=self.children_has_normalizer,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=self.types_field.types,
            normalizer=self.normalizer_field.finals,
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.types_field.types,
            tags=self.tags_field.finals,
            children_tags={tag.final for tag in self.children_tags},
        )
        self.my_type = set(self.types_field.types)
        return exceptions
