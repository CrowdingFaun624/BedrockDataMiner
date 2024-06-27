import enum

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.OptionalFunctionField as OptionalFunctionField
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.DictStructure as DictStructure
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class DictSorting(enum.Enum):
    none = "none"
    by_key = "by_key"
    by_value = "by_value"

class DictComponent(StructureComponent.StructureComponent[DictStructure.DictStructure]):

    class_name_article = "a Dict"
    class_name = "Dict"
    my_capabilities = Capabilities.Capabilities(has_keys=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("comparison_move_function", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("min_key_similarity_threshold", "a float", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("min_value_similarity_threshold", "a float", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("sort", "a str", False, TypeVerifier.EnumTypeVerifier([item.value for item in DictSorting])),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.DictTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.detect_key_moves = data.get("detect_key_moves", False)
        self.field = data.get("field", "field")
        self.measure_length = data.get("measure_length", False)
        self.min_key_similarity_threshold = data.get("min_key_similarity_threshold", DictStructure.MIN_KEY_SIMILARITY_THRESHOLD)
        self.min_value_similarity_threshold = data.get("min_value_similarity_threshold", DictStructure.MIN_VALUE_SIMILARITY_THRESHOLD)
        self.print_all = data.get("print_all", False)
        self.sort = DictSorting[data.get("sort", "none")]

        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(data["subcomponent"], ["subcomponent"])
        self.comparison_move_function_field = OptionalFunctionField.OptionalFunctionField(data.get("comparison_move_function", None), ["comparison_move_function"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "dict"), ["this_type"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.tags_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        if self.sort == DictSorting.by_value:
            self.types_field.must_be(StructureComponent.SORTABLE_TYPES)
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.this_type_field.must_be(StructureComponent.MAPPING_TYPES)
        self.fields.extend([self.subcomponent_field, self.comparison_move_function_field, self.normalizer_field, self.this_type_field, self.types_field, self.tags_field])

    def create_final(self) -> None:
        super().create_final()
        match self.sort:
            case DictSorting.none:
                sorting_function = None
            case DictSorting.by_key:
                sorting_function = lambda item: item[0]
            case DictSorting.by_value:
                sorting_function = lambda item: item[1]
        self.final = DictStructure.DictStructure(
            name=self.name,
            field=self.field,
            detect_key_moves=self.detect_key_moves,
            comparison_move_function=self.comparison_move_function_field.get_function(),
            measure_length=self.measure_length,
            print_all=self.print_all,
            sorting_function=sorting_function,
            min_key_similarity_threshold=self.min_key_similarity_threshold,
            min_value_similarity_threshold=self.min_value_similarity_threshold,
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
        self.my_type = set(self.this_type_field.get_types())

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.sort == DictSorting.by_value and len(self.types_field) > 0:
            first_type = self.types_field.get_types()[0]
            for category in StructureComponent.MUTUALLY_SORTABLE:
                if first_type not in category: continue
                exceptions.extend(
                    Exceptions.ComponentTypeInvalidTypeError(self, type, category)
                    for type in self.types_field.get_types()
                    if type not in category
                )
                break
        return exceptions
