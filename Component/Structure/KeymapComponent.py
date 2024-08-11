import enum

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.FieldListField as FieldListField
import Component.Structure.Field.KeymapImportField as KeymapImportField
import Component.Structure.Field.KeymapKeyField as KeymapKeyField
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.Difference as D
import Structure.KeymapStructure as KeymapStructure
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class KeymapSorting(enum.Enum):
    none = "none"
    by_key = "by_key"
    by_value = "by_value"
    by_component_order = "by_component_order"

class KeymapComponent(StructureComponent.StructureComponent[KeymapStructure.KeymapStructure]):

    class_name_article = "a Keymap"
    class_name = "Keymap"
    my_capabilities = Capabilities.Capabilities(has_importable_keys=True, has_keys=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_component", "a str, StructureComponent or None", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_weight", "a float", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("keys", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
            TypeVerifier.TypedDictKeyTypeVerifier("required", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent, or None", False, (str, dict, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("weight", "a int", False, int, lambda key, value: (value >= 0, "must be at least 0")),
        ), "a dict", "a str", "a dict")),
        TypeVerifier.TypedDictKeyTypeVerifier("min_key_similarity_threshold", "a float", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("min_value_similarity_threshold", "a float", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("sort", "a str", False, TypeVerifier.EnumTypeVerifier([item.value for item in KeymapSorting])),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("value_weight", "a float", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
    )

    def __init__(self, data:ComponentTyping.KeymapTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.detect_key_moves = data.get("detect_key_moves", False)
        self.min_key_similarity_threshold = data.get("min_key_similarity_threshold", KeymapStructure.MIN_KEY_SIMILARITY_THRESHOLD)
        self.min_value_similarity_threshold = data.get("min_value_similarity_threshold", KeymapStructure.MIN_VALUE_SIMILARITY_THRESHOLD)
        self.key_weight = data.get("key_weight", KeymapStructure.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", KeymapStructure.VALUE_WEIGHT)
        self.sort = KeymapSorting[data.get("sort", "none")]

        self.import_field = KeymapImportField.KeymapImportField(data.get("imports", []), ["imports"])
        self.keys = FieldListField.FieldListField([KeymapKeyField.KeymapKeyField(key_data, key, self.children_tags, ["keys", key], self) for key, key_data in data["keys"].items()], ["keys"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), ["delegate"])
        self.key_structure_field = OptionalStructureComponentField.OptionalStructureComponentField(data.get("key_component", None), ["key_component"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.tags_for_all_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "dict"), ["this_type"])
        if self.sort == KeymapSorting.by_value:
            self.keys.for_each(lambda keymap_key_field: keymap_key_field.types_field.must_be(StructureComponent.SORTABLE_TYPES))
        self.tags_for_all_field.add_to_tag_set(self.children_tags)
        self.keys.for_each(lambda key: key.add_tag_fields(self.tags_for_all_field))
        self.import_field.import_into(self.keys)
        self.this_type_field.must_be(StructureComponent.MAPPING_TYPES)
        self.fields.extend([self.import_field, self.delegate_field, self.key_structure_field, self.tags_for_all_field, self.keys, self.this_type_field, self.normalizer_field, self.pre_normalized_types_field, self.post_normalizer_field])

    def create_final(self) -> None:
        super().create_final()
        match self.sort:
            case KeymapSorting.none:
                sorting_function = None
            case KeymapSorting.by_key:
                sorting_function = lambda item: item[0]
            case KeymapSorting.by_value:
                sorting_function = lambda item: item[1]
            case KeymapSorting.by_component_order:
                key_order = {key.key: index for index, key in enumerate(self.keys)}
                sorting_function = lambda item: key_order[key.first_existing_property()] if isinstance((key := item[0]), D.Diff) else key_order[key]
        self.final = KeymapStructure.KeymapStructure(
            name=self.name,
            sorting_function=sorting_function,
            detect_key_moves=self.detect_key_moves,
            min_key_similarity_threshold=self.min_key_similarity_threshold,
            min_value_similarity_threshold=self.min_value_similarity_threshold,
            key_weight=self.key_weight,
            value_weight=self.value_weight,
            key_weights={key.key: key.weight for key in self.keys},
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        delegate_keys_arguments = {key.key: key.delegate_arguments for key in self.keys}
        self.get_final().link_substructures(
            keys={key.key: key.get_subcomponent() for key in self.keys},
            delegate=self.delegate_field.create_delegate(self.get_final(), delegate_keys_arguments),
            key_types={key.key: key.get_types() for key in self.keys},
            key_structure=self.key_structure_field.get_final(),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else self.this_type_field.get_types(),
            tags={keymap_field.key: keymap_field.tags_field.get_finals() for keymap_field in self.keys},
            keys_with_normalizers=[key.key for key in self.keys if (subcomponent := key.get_subcomponent()) is not None and subcomponent.children_has_normalizer] if self.children_has_normalizer else [],
            required_keys=[key.key for key in self.keys if key.required],
        )
        self.my_type = set(self.this_type_field.get_types())

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.sort == KeymapSorting.by_value and len(self.keys) > 0:
            types_set:set[type] = set()
            types_list:list[type] = []
            for key in self.keys:
                for key_type in key.get_types():
                    if key_type in types_set: continue
                    types_set.add(key_type)
                    types_list.append(key_type)
            first_type = types_list[0]
            for category in StructureComponent.MUTUALLY_SORTABLE:
                if first_type not in category: continue
                exceptions.extend(
                    Exceptions.ComponentTypeInvalidTypeError(self, type, category)
                    for type in types_list
                    if type not in category
                )
                break
        return exceptions
