import Structure.CacheStructure as CacheStructure
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.StructureComponent as StructureComponent
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])

class CacheComponent(StructureComponent.StructureComponent):

    class_name_article = "a Cache"
    class_name = "Cache"
    my_properties = ComponentCapabilities.Capabilities(is_structure=True)
    final:CacheStructure.CacheStructure
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_check_all_types", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_normalize", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_get_tag_paths", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_compare_text", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_print_text", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("cache_compare", "a bool", False, bool),
    )

    def __init__(self, data:ComponentTyping.CacheComponentTypedDict, name: str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.cache_check_all_types = data.get("cache_check_all_types", True)
        self.cache_normalize = data.get("cache_normalize", True)
        self.cache_get_tag_paths = data.get("cache_get_tag_paths", True)
        self.cache_compare_text = data.get("cache_compare_text", True)
        self.cache_print_text = data.get("cache_print_text", True)
        self.cache_compare = data.get("cache_compare", True)

        self.subcomponent_field:OptionalComponentField.OptionalComponentField[StructureComponent.StructureComponent] = OptionalComponentField.OptionalComponentField(data["subcomponent"], COMPONENT_REQUEST_PROPERTIES, ["subcomponent"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.fields.extend([self.subcomponent_field, self.types_field])

    def create_final(self) -> None:
        types_final = self.types_field.get_types()
        self.my_type = types_final
        self.final = CacheStructure.CacheStructure(
            name=self.name,
            structure=None,
            types=tuple(types_final),
            cache_check_all_types=self.cache_check_all_types,
            cache_normalize=self.cache_normalize,
            cache_get_tag_paths=self.cache_get_tag_paths,
            cache_compare_text=self.cache_compare_text,
            cache_print_text=self.cache_print_text,
            cache_compare=self.cache_compare,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        assert self.final is not None
        structure = self.subcomponent_field.get_component()
        assert structure is not None
        self.final.structure = structure.final

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions = super().check(config)
        subcomponent = self.subcomponent_field.get_component()
        types = self.types_field.get_types()
        if subcomponent is None:
            for value_type in types:
                if value_type in ComponentTyping.REQUIRES_SUBCOMPONENT_TYPES:
                    exceptions.append((TypeError("%s \"%s\" accepts type %s, but has a null Subcomponent!" % (self.class_name, self.name, value_type.__name__))))
        else:
            if set(types) != set(subcomponent.my_type):
                my_types = ", ".join(type_item.__name__ for type_item in types)
                its_types = ", ".join(type_item.__name__ for type_item in subcomponent.my_type)
                exceptions.append(TypeError("%s \"%s\" accepts types [%s], but its Subcomponent, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, my_types, subcomponent.name, its_types)))
        return exceptions