import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.StringStructure as StringStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class StringComponent(StructureComponent.StructureComponent[StringStructure.StringStructure]):

    class_name = "String"
    class_name_article = "a String"
    my_capabilities = Capabilities.Capabilities(is_primitive=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.PrimitiveComponentTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)

        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.tags_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field = TypeListField.TypeListField(data.get("types", "str"), ["types"])
        self.types_field.must_be(StructureComponent.STRING_TYPES)
        self.fields.extend([self.normalizer_field, self.tags_field, self.types_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = StringStructure.StringStructure(
            name=self.name,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_substructures(
            types=tuple(self.types_field.get_types()),
            normalizer=self.normalizer_field.get_finals(),
            tags=self.tags_field.get_tags(),
        )
        self.my_type = set(self.types_field.get_types())
