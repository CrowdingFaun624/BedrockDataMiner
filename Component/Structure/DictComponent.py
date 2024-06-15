import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.OptionalFunctionField as OptionalFunctionField
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalStructroidComponentField as OptionalStructroidComponentField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.DictStructure as DictStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class DictComponent(StructureComponent.StructureComponent[DictStructure.DictStructure]):

    class_name_article = "a Dict"
    class_name = "Dict"
    my_type = [dict]
    my_capabilities = Capabilities.Capabilities(has_keys=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructroidComponent or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("comparison_move_function", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.DictTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
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
        super().create_final()
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
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            types=self.types_field.get_types(),
            normalizer=self.normalizer_field.get_finals(),
            tags=self.tags_field.get_finals()
        )
