import enum

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
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
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("key_component", "a str, StructureComponent or None", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_weight", "a float", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("max_key_similarity_descendent_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("min_key_similarity_threshold", "a float", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("min_value_similarity_threshold", "a float", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("required_keys", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("sort", "a str", False, TypeVerifier.EnumTypeVerifier([item.value for item in DictSorting])),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("value_weight", "a float", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
    )

    def __init__(self, data:ComponentTyping.DictTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)

        self.detect_key_moves = data.get("detect_key_moves", True)
        self.min_key_similarity_threshold = data.get("min_key_similarity_threshold", DictStructure.MIN_KEY_SIMILARITY_THRESHOLD)
        self.min_value_similarity_threshold = data.get("min_value_similarity_threshold", DictStructure.MIN_VALUE_SIMILARITY_THRESHOLD)
        self.key_weight = data.get("key_weight", DictStructure.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", DictStructure.VALUE_WEIGHT)
        self.sort = DictSorting[data.get("sort", "none")]
        self.required_keys = data.get("required_keys", [])
        self.max_key_similarity_descendent_depth = data.get("max_key_similarity_descendent_depth", 6)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 6)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(data["subcomponent"], ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), ["delegate"])
        self.key_structure_field = OptionalStructureComponentField.OptionalStructureComponentField(data.get("key_component", None), ["key_component"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "dict"), ["this_type"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.tags_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        if self.sort == DictSorting.by_value:
            self.types_field.must_be(StructureComponent.SORTABLE_TYPES)
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.this_type_field.must_be(StructureComponent.MAPPING_TYPES)
        self.fields.extend([self.subcomponent_field, self.delegate_field, self.key_structure_field, self.normalizer_field, self.pre_normalized_types_field, self.this_type_field, self.types_field, self.tags_field, self.post_normalizer_field])

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
            detect_key_moves=self.detect_key_moves,
            sorting_function=sorting_function,
            max_key_similarity_descendent_depth=self.max_key_similarity_descendent_depth,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            min_key_similarity_threshold=self.min_key_similarity_threshold,
            min_value_similarity_threshold=self.min_value_similarity_threshold,
            key_weight=self.key_weight,
            value_weight=self.value_weight,
            children_has_normalizer=self.children_has_normalizer,
            children_has_garbage_collection=self.children_has_garbage_collection,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            delegate=self.delegate_field.create_delegate(self.get_final(), exceptions=exceptions),
            key_structure=self.key_structure_field.get_final(),
            types=self.types_field.get_types(),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else self.this_type_field.get_types(),
            tags=self.tags_field.get_finals(),
            required_keys=self.required_keys,
            children_tags={tag.get_final() for tag in self.children_tags},
        )
        self.my_type = set(self.this_type_field.get_types())
        return exceptions

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
