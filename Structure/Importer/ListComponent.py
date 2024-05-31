import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.NormalizerListField as NormalizerListField
import Structure.Importer.Field.OptionalStructroidComponentField as OptionalStructroidComponentField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.StructureComponent as StructureComponent
import Structure.ListStructure as ListStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class ListComponent(StructureComponent.StructureComponent):

    class_name_article = "a List"
    class_name = "List"
    my_type = [list]
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    final:ListStructure.ListStructure
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("ordered", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_flat", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.ListComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.field = data.get("field", "item")
        self.measure_length = data.get("measure_length", False)
        self.ordered = data.get("ordered", True)
        self.print_all = data.get("print_all", False)
        self.print_flat = data.get("print_flat", False)

        self.subcomponent_field = OptionalStructroidComponentField.OptionalStructroidComponentField(data["subcomponent"], ["subcomponent"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.normalizer_field:NormalizerListField.NormalizerListField = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.fields.extend([self.subcomponent_field, self.types_field, self.normalizer_field, self.tags_field])

    def create_final(self) -> None:
        self.final = ListStructure.ListStructure(
            name=self.name,
            field=self.field,
            print_flat=self.print_flat,
            print_all=self.print_all,
            measure_length=self.measure_length,
            ordered=self.ordered,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        assert self.final is not None
        self.final.link_substructures(
            structure=self.subcomponent_field.get_final(),
            types=self.types_field.get_types(),
            normalizer=self.normalizer_field.get_finals(),
            tags=self.tags_field.get_finals()
        )
