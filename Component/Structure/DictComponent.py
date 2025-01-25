import enum
from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Structure.Field.DelegateField as DelegateField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.DictStructure as DictStructure
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier


class DictSorting(enum.Enum):
    none = "none"
    by_key = "by_key"
    by_value = "by_value"

class DictComponent(StructureComponent.StructureComponent[DictStructure.DictStructure]):

    class_name = "Dict"
    my_capabilities = Capabilities.Capabilities(has_keys=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("key_component", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_weight", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("max_key_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("min_key_similarity_threshold", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("min_value_similarity_threshold", False, float, lambda key, value: (value > 0.0 and value <= 1.0, "must be in the range (0.0,1.0]")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("required_keys", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("sort", False, TypeVerifier.EnumTypeVerifier([item.value for item in DictSorting])),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("value_weight", False, float, lambda key, value: (value >= 0.0 and value <= 1.0, "must be in the range [0.0,1.0]")),
    )

    __slots__ = (
        "delegate_field",
        "detect_key_moves",
        "key_structure_field",
        "key_weight",
        "max_key_similarity_descendent_depth",
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "min_key_similarity_threshold",
        "min_value_similarity_threshold",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "required_keys",
        "sort",
        "subcomponent_field",
        "tags_field",
        "this_type_field",
        "types_field",
        "value_weight",
    )

    def initialize_fields(self, data: ComponentTyping.DictTypedDict) -> Sequence[Field.Field]:
        self.detect_key_moves = data.get("detect_key_moves", True)
        self.min_key_similarity_threshold = data.get("min_key_similarity_threshold", DictStructure.MIN_KEY_SIMILARITY_THRESHOLD)
        self.min_value_similarity_threshold = data.get("min_value_similarity_threshold", DictStructure.MIN_VALUE_SIMILARITY_THRESHOLD)
        self.key_weight = data.get("key_weight", DictStructure.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", DictStructure.VALUE_WEIGHT)
        self.sort = DictSorting[data.get("sort", "none")]
        self.required_keys:Sequence[str] = data.get("required_keys", ())
        self.max_key_similarity_descendent_depth = data.get("max_key_similarity_descendent_depth", 6)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 6)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponent_field = ComponentField.OptionalComponentField(data["subcomponent"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("subcomponent",))
        self.delegate_field = DelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.key_structure_field = ComponentField.OptionalComponentField(data.get("key_component", None), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("key_component",))
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("post_normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "dict"), ("this_type",)).must_be(self.domain.type_stuff.mapping_types).add_to_set(self.my_type)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",))
        self.tags_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags)
        self.types_field = TypeListField.TypeListField(data["types"], ("types",)).verify_with(self.subcomponent_field).conditional_must_be(self.sort == DictSorting.by_value, self.domain.type_stuff.sortable_types)
        return (self.subcomponent_field, self.delegate_field, self.key_structure_field, self.normalizer_field, self.pre_normalized_types_field, self.this_type_field, self.types_field, self.tags_field, self.post_normalizer_field)

    def create_final(self) -> DictStructure.DictStructure:
        match self.sort:
            case DictSorting.none:
                sorting_function = None
            case DictSorting.by_key:
                sorting_function = lambda item: item[0]
            case DictSorting.by_value:
                sorting_function = lambda item: item[1]
        return DictStructure.DictStructure(
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
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            structure=self.subcomponent_field.map(lambda subcomponent: subcomponent.final),
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            key_structure=self.key_structure_field.map(lambda subcomponent: subcomponent.final),
            types=self.types_field.types,
            normalizer=tuple(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=tuple(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.this_type_field.types,
            tags=self.tags_field.finals,
            required_keys=self.required_keys,
            children_tags={tag.final for tag in self.children_tags},
        )
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.sort == DictSorting.by_value and len(self.types_field) > 0:
            first_type = self.types_field.types[0]
            for category_name, category_types in self.domain.type_stuff.mutually_sortable.items():
                if first_type not in category_types: continue
                exceptions.extend(
                    Exceptions.ComponentTypeInvalidTypeError(self, type, category_types, message=f"(in sortable category \"{category_name}\")")
                    for type in self.types_field.types
                    if type not in category_types
                )
                break
        return exceptions
