import Structure.CacheStructure as CacheStructure
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentField as ComponentField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.StructureComponent as StructureComponent
import Utilities.TypeVerifier as TypeVerifier
from Structure.Importer.ImporterConfig import ImporterConfig

COMPONENT_REQUEST_PROPERTIES:ComponentCapabilities.CapabilitiesPattern[StructureComponent.StructureComponent|GroupComponent.GroupComponent] = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])

class CacheComponent(StructureComponent.StructureComponent):

    class_name_article = "a Cache"
    class_name = "Cache"
    my_properties = ComponentCapabilities.Capabilities(is_structure=True)
    final:CacheStructure.CacheStructure
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a list or str", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
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

        self.subcomponent_field = ComponentField.ComponentField(data["subcomponent"], COMPONENT_REQUEST_PROPERTIES, ["subcomponent"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.types_field.verify_with(self.subcomponent_field)
        self.fields.extend([self.subcomponent_field, self.types_field])

    def create_final(self) -> None:
        self.final = CacheStructure.CacheStructure(
            name=self.name,
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
        super().link_finals()
        assert self.final is not None
        subcomponent = self.subcomponent_field.get_component()
        assert subcomponent.final is not None
        types = self.types_field.get_types()
        self.my_type = types
        self.final.link_substructures(
            structure=subcomponent.final,
            types=types,
        )

    def check(self, config: ImporterConfig) -> list[Exception]:
        exceptions = super().check(config)
        structure = self.subcomponent_field.get_component().final
        if isinstance(structure, dict):
            exceptions.extend(ValueError("%s %s cannot except null subcomponent in type %s: null" % (self.class_name, self.name, substructure_type.__name__)) for substructure_type, substructure in structure.items() if substructure is None)
        return exceptions
