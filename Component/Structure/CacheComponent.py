import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.StructureComponentField as StructureComponentField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.CacheStructure as CacheStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class CacheComponent(StructureComponent.StructureComponent[CacheStructure.CacheStructure]):

    class_name_article = "a Cache"
    class_name = "Cache"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("cache_check_all_types", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_compare", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_compare_text", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_get_similarity", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_get_tag_paths", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_normalize", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_print_text", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a list or str", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.CacheTypedDict, name: str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.cache_check_all_types = data.get("cache_check_all_types", True)
        self.cache_normalize = data.get("cache_normalize", True)
        self.cache_get_tag_paths = data.get("cache_get_tag_paths", True)
        self.cache_compare_text = data.get("cache_compare_text", True)
        self.cache_print_text = data.get("cache_print_text", True)
        self.cache_get_similarity = data.get("cache_get_similarity", True)
        self.cache_compare = data.get("cache_compare", True)

        self.subcomponent_field = StructureComponentField.StructureComponentField(data["subcomponent"], ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultDelegate"), data.get("delegate_arguments", {}), ["delegate"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.types_field.verify_with(self.subcomponent_field)
        self.fields.extend([self.subcomponent_field, self.delegate_field, self.types_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = CacheStructure.CacheStructure(
            name=self.name,
            cache_check_all_types=self.cache_check_all_types,
            cache_normalize=self.cache_normalize,
            cache_get_tag_paths=self.cache_get_tag_paths,
            cache_compare_text=self.cache_compare_text,
            cache_print_text=self.cache_print_text,
            cache_get_similarity=self.cache_get_similarity,
            cache_compare=self.cache_compare,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        types = self.types_field.get_types()
        self.my_type = set(types)
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            delegate=self.delegate_field.create_delegate(self.get_final()),
            types=types,
        )
        return exceptions
