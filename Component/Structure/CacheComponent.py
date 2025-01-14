import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.CacheStructure as CacheStructure
import Utilities.TypeVerifier as TypeVerifier


class CacheComponent(StructureComponent.StructureComponent[CacheStructure.CacheStructure]):

    class_name = "Cache"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("cache_check_all_types", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_compare", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_compare_text", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_get_similarity", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_get_tag_paths", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_normalize", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_print_text", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_threshold", False, int),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    )

    __slots__ = (
        "cache_check_all_types",
        "cache_compare",
        "cache_compare_text",
        "cache_get_referenced_files",
        "cache_get_similarity",
        "cache_get_tag_paths",
        "cache_normalize",
        "cache_print_text",
        "delegate_field",
        "my_type",
        "subcomponent_field",
        "remove_threshold",
        "types_field",
    )

    def initialize_fields(self, data: ComponentTyping.CacheTypedDict) -> list[Field.Field]:
        self.remove_threshold = data.get("remove_threshold", 10)
        self.cache_check_all_types = data.get("cache_check_all_types", True)
        self.cache_normalize = data.get("cache_normalize", True)
        self.cache_get_tag_paths = data.get("cache_get_tag_paths", True)
        self.cache_get_referenced_files = data.get("cache_get_referenced_files", True)
        self.cache_compare_text = data.get("cache_compare_text", True)
        self.cache_print_text = data.get("cache_print_text", True)
        self.cache_get_similarity = data.get("cache_get_similarity", True)
        self.cache_compare = data.get("cache_compare", True)

        self.subcomponent_field = ComponentField.ComponentField(data["subcomponent"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), self.domain, ["delegate"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"]).verify_with(self.subcomponent_field)
        return [self.subcomponent_field, self.delegate_field, self.types_field]

    def create_final(self) -> CacheStructure.CacheStructure:
        return CacheStructure.CacheStructure(
            name=self.name,
            cache_remove_threshold=self.remove_threshold,
            cache_check_all_types=self.cache_check_all_types,
            cache_normalize=self.cache_normalize,
            cache_get_tag_paths=self.cache_get_tag_paths,
            cache_get_referenced_files=self.cache_get_referenced_files,
            cache_compare_text=self.cache_compare_text,
            cache_print_text=self.cache_print_text,
            cache_get_similarity=self.cache_get_similarity,
            cache_compare=self.cache_compare,
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        types = self.types_field.types
        self.my_type = set(types)
        self.final.link_substructures(
            structure=self.subcomponent_field.subcomponent.final,
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=types,
            children_tags={tag.final for tag in self.children_tags},
        )
        return exceptions
