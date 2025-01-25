import enum
from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Structure.Field.KeymapImportField as KeymapImportField
import Component.Structure.Field.KeymapKeyField as KeymapKeyField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.Difference as D
import Structure.KeymapStructure as KeymapStructure
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier


class KeymapSorting(enum.Enum):
    none = "none"
    by_key = "by_key"
    by_value = "by_value"
    by_component_order = "by_component_order"

class KeymapComponent(StructureComponent.StructureComponent[KeymapStructure.KeymapStructure]):

    class_name = "Keymap"
    my_capabilities = Capabilities.Capabilities(has_importable_keys=True, has_keys=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("default_max_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_component", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_weight", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("keys", False, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
            TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", False, (int, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("required", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", False, (str, dict, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
            TypeVerifier.TypedDictKeyTypeVerifier("weight", False, int, lambda key, value: (value >= 0, "must be at least 0")),
        ))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_key_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("min_key_similarity_threshold", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("min_value_similarity_threshold", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("sort", False, TypeVerifier.EnumTypeVerifier([item.value for item in KeymapSorting])),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("value_weight", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
    )

    __slots__ = (
        "default_max_similarity_descendent_depth",
        "delegate_field",
        "detect_key_moves",
        "import_field",
        "key_structure_field",
        "key_weight",
        "keys",
        "max_key_similarity_descendent_depth",
        "max_similarity_ancestor_depth",
        "min_key_similarity_threshold",
        "min_value_similarity_threshold",
        "my_type",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "sort",
        "tags_for_all_field",
        "this_type_field",
        "value_weight",
    )

    def initialize_fields(self, data: ComponentTyping.KeymapTypedDict) -> Sequence[Field.Field]:
        self.detect_key_moves = data.get("detect_key_moves", False)
        self.min_key_similarity_threshold = data.get("min_key_similarity_threshold", KeymapStructure.MIN_KEY_SIMILARITY_THRESHOLD)
        self.min_value_similarity_threshold = data.get("min_value_similarity_threshold", KeymapStructure.MIN_VALUE_SIMILARITY_THRESHOLD)
        self.key_weight = data.get("key_weight", KeymapStructure.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", KeymapStructure.VALUE_WEIGHT)
        self.sort = KeymapSorting[data.get("sort", "none")]
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)
        self.max_key_similarity_descendent_depth = data.get("max_key_similarity_descendent_depth", 4)
        self.default_max_similarity_descendent_depth = data.get("default_max_similarity_descendent_depth", None)

        self.tags_for_all_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.keys = FieldListField.FieldListField([
            KeymapKeyField.KeymapKeyField(key_data, key, self.children_tags, ("keys", key), self)
                .conditional_must_be(self.sort == KeymapSorting.by_value, self.domain.type_stuff.sortable_types)
                .add_tag_fields(self.tags_for_all_field)
            for key, key_data in data.get("keys", {}).items()
        ], ("keys",))
        self.import_field = KeymapImportField.KeymapImportField(data.get("imports", ()), ("imports",)).import_into(self.keys)
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.key_structure_field = OptionalComponentField.OptionalComponentField(data.get("key_component"), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("key_component",))
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("post_normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",))
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "dict"), ("this_type",)).must_be(self.domain.type_stuff.mapping_types)
        return (self.import_field, self.delegate_field, self.key_structure_field, self.tags_for_all_field, self.keys, self.this_type_field, self.normalizer_field, self.pre_normalized_types_field, self.post_normalizer_field)

    def create_final(self) -> KeymapStructure.KeymapStructure:
        match self.sort:
            case KeymapSorting.none:
                sorting_function = None
            case KeymapSorting.by_key:
                sorting_function = lambda item: item[0]
            case KeymapSorting.by_value:
                sorting_function = lambda item: item[1]
            case KeymapSorting.by_component_order:
                key_order = {key.key: index for index, key in enumerate(self.keys)}
                sorting_function = lambda item: key_order[key.last_value] if isinstance((key := item[0]), D.Diff) else key_order[key]
        return KeymapStructure.KeymapStructure(
            name=self.name,
            sorting_function=sorting_function,
            detect_key_moves=self.detect_key_moves,
            min_key_similarity_threshold=self.min_key_similarity_threshold,
            min_value_similarity_threshold=self.min_value_similarity_threshold,
            key_weight=self.key_weight,
            value_weight=self.value_weight,
            key_weights={key.key: key.weight for key in self.keys},
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            default_max_similarity_descendent_depth=self.default_max_similarity_descendent_depth,
            max_key_similarity_descendent_depth=self.max_key_similarity_descendent_depth,
            keys_max_similarity_descendent_depth={key.key: key.max_similarity_descendent_depth for key in self.keys if key.max_similarity_descendent_depth is not ...},
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        delegate_keys_arguments = {key.key: key.delegate_arguments for key in self.keys}
        self.final.link_substructures(
            keys={key.key: key.subcomponent_field.get_final(lambda subcomponent: subcomponent.final) for key in self.keys},
            delegate=self.delegate_field.create_delegate(self.final, delegate_keys_arguments, exceptions=exceptions),
            key_types={key.key: key.types_field.types for key in self.keys},
            key_structure=self.key_structure_field.get_final(lambda subcomponent: subcomponent.final),
            normalizer=tuple(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=tuple(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.this_type_field.types,
            tags={keymap_field.key: keymap_field.tags_field.finals for keymap_field in self.keys},
            required_keys=[key.key for key in self.keys if key.required],
            children_tags={tag.final for tag in self.children_tags},
        )
        self.my_type = set(self.this_type_field.types)
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.sort == KeymapSorting.by_value and len(self.keys) > 0:
            types_set:set[type] = set()
            types_list:list[type] = []
            for key in self.keys:
                for key_type in key.types_field.types:
                    if key_type in types_set: continue
                    types_set.add(key_type)
                    types_list.append(key_type)
            first_type = types_list[0]
            for category_name, category_types in self.domain.type_stuff.mutually_sortable.items():
                if first_type not in category_types: continue
                exceptions.extend(
                    Exceptions.ComponentTypeInvalidTypeError(self, type, category_types, message=f"(in sortable category \"{category_name}\")")
                    for type in types_list
                    if type not in category_types
                )
                break
        return exceptions
