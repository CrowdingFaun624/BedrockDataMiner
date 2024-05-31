import Structure.DictStructure as DictStructure
import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.NormalizerListField as NormalizerListField
import Structure.Importer.Field.OptionalFunctionField as OptionalFunctionField
import Structure.Importer.Field.OptionalStructroidComponentField as OptionalStructroidComponentField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.StructureComponent as StructureComponent
import Utilities.TypeVerifier as TypeVerifier


class DictComponent(StructureComponent.StructureComponent):

    class_name_article = "a Dict"
    class_name = "Dict"
    my_type = [dict]
    my_capabilities = Capabilities.Capabilities(has_keys=True, is_structure=True)
    final:DictStructure.DictStructure
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("comparison_move_function", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.DictComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.detect_key_moves = data.get("detect_key_moves", False)
        self.field = data.get("field", "field")
        self.measure_length = data.get("measure_length", False)
        self.print_all = data.get("print_all", False)

        self.subcomponent_field = OptionalStructroidComponentField.OptionalStructroidComponentField(data["subcomponent"], ["subcomponent"])
        self.comparison_move_function_field = OptionalFunctionField.OptionalFunctionField(data.get("comparison_move_function", None), ["comparison_move_function"])
        self.normalizer_field:NormalizerListField.NormalizerListField = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.fields.extend([self.subcomponent_field, self.comparison_move_function_field, self.normalizer_field, self.types_field, self.tags_field])

    def create_final(self) -> None:
        self.final = DictStructure.DictStructure(
            name=self.name,
            field=self.field,
            detect_key_moves=self.detect_key_moves,
            comparison_move_function=self.comparison_move_function_field.get_function(),
            measure_length=self.measure_length,
            print_all=self.print_all,
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
