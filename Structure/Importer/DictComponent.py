import Structure.DictStructure as DictStructure
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.NormalizerListField as NormalizerListField
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.Field.OptionalFunctionField as OptionalFunctionField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.StructureComponent as StructureComponent
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])

class DictComponent(StructureComponent.StructureComponent):

    class_name_article = "a Dict"
    class_name = "Dict"
    my_type = [dict]
    my_properties = ComponentCapabilities.Capabilities(has_keys=True, is_structure=True)
    final:DictStructure.DictStructure
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("comparison_move_function", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def __init__(self, data:ComponentTyping.DictComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.detect_key_moves = data.get("detect_key_moves", False)
        self.field = data.get("field", "field")
        self.measure_length = data.get("measure_length", False)
        self.print_all = data.get("print_all", False)

        self.subcomponent_field:OptionalComponentField.OptionalComponentField[StructureComponent.StructureComponent|GroupComponent.GroupComponent] = OptionalComponentField.OptionalComponentField(data["subcomponent"], COMPONENT_REQUEST_PROPERTIES, ["subcomponent"])
        self.comparison_move_function_field = OptionalFunctionField.OptionalFunctionField(data.get("comparison_move_function", None), ["comparison_move_function"])
        self.normalizer_field:NormalizerListField.NormalizerListField = NormalizerListField.NormalizerListField([] if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"]), ["normalizer"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.fields.extend([self.subcomponent_field, self.comparison_move_function_field, self.normalizer_field, self.types_field, self.tags_field])

    def create_final(self) -> None:
        self.final = DictStructure.DictStructure(
            name=self.name,
            field=self.field,
            types=tuple(self.types_field.get_types()),
            detect_key_moves=self.detect_key_moves,
            comparison_move_function=self.comparison_move_function_field.get_function(),
            measure_length=self.measure_length,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        assert self.final is not None
        self.final.link_substructures(
            structure=subcomponent.final if (subcomponent := self.subcomponent_field.get_component()) is not None else None,
            normalizer=self.normalizer_field.get_finals(),
            tags=self.tags_field.get_finals()
        )
