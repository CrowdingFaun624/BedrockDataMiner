from typing import Callable, cast

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.FieldListField as FieldListField
import Structure.Importer.Field.KeymapKeyField as KeymapKeyField
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TagComponent as TagComponent
import Structure.KeymapStructure as KeymapStructure
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Utilities.TypeVerifier as TypeVerifier

IMPORTABLE_KEYS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"has_importable_keys": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])
TAG_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_tag": True}])

class KeymapComponent(StructureComponent.StructureComponent):

    class_name_article = "a Keymap"
    class_name = "Keymap"

    my_type = [dict]

    my_properties = ComponentCapabilities.Capabilities(has_importable_keys=True, has_keys=True, is_structure=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("keys", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", False, (str, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        ), "a dict", "a str", "a dict")),
    )

    def __init__(self, data:ComponentTyping.KeymapComponentTypedDict, name:str) -> None:
        self.verify_arguments(data, name)

        self.name = name
        self.field = data.get("field", "field")
        self.imports = [] if "imports" not in data else ([data["imports"]] if isinstance(data["imports"], str) else data["imports"])
        self.measure_length = data.get("measure_length", False)
        self.print_all = data.get("print_all", False)

        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.tags:dict[str,list[TagComponent.TagComponent]]|None = None
        self.final:KeymapStructure.KeymapStructure|None = None
        self.keys_final:dict[tuple[str,type],Structure.Structure|None] = {}

        self.children_has_normalizer = self.children_has_normalizer_default
        self.children_tags:set[str] = set()

        self.keys = FieldListField.FieldListField([KeymapKeyField.KeymapKeyField(key_data, key, ["keys", key]) for key, key_data in data["keys"].items()], ["keys"])
        self.normalizer_field:ComponentListField.ComponentListField[NormalizerComponent.NormalizerComponent] = ComponentListField.ComponentListField([] if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"]), NORMALIZER_REQUEST_PROPERTIES, ["normalizer"])
        self.tags_for_all_field:ComponentListField.ComponentListField[TagComponent.TagComponent] = ComponentListField.ComponentListField(data.get("tags", []), TAG_REQUEST_PROPERTIES, ["tags"])
        self.fields = [self.keys, self.normalizer_field, self.tags_for_all_field]

    def set_imports(self, components:dict[str,Component.Component], imports:list[str]) -> None:
        keymap_components:list[KeymapComponent] = []
        for index, imported_component_str in enumerate(imports):
            keymap_component = Field.choose_component(imported_component_str, IMPORTABLE_KEYS_REQUEST_PROPERTIES, components, ["imports", index], self.name, self.class_name, KeymapComponent)
            keymap_components.append(keymap_component)
            self.keys.extend_from_field_list(keymap_component.keys)
        self.link_components(keymap_components)

    def set_component(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        self.set_imports(components, self.imports)
        super().set_component(components, functions)
        self.keys.for_each(lambda keymap_key_field: keymap_key_field.add_tag_fields(self.tags_for_all_field))
        self.children_tags.update(self.tags_for_all_field.map(lambda tag_component: tag_component.name))
        for tag_list in self.keys.map(lambda keymap_key_field: (tag_component.name for tag_component in keymap_key_field.tags_field.get_components())):
            self.children_tags.update(tag_list)

    def create_final_get_final_normalizers(self) -> list[Normalizer.Normalizer]|None:
        return None if len(self.normalizer_field) == 0 else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizer_field.get_components()]

    def create_final_get_tags_final(self) -> dict[str,list[str]]:
        return {key: [tag_component.name for tag_component in tag_components] for key, tag_components in self.keys.map(lambda keymap_field: (keymap_field.key, keymap_field.tags_field.get_components()))}

    def create_final(self) -> None:
        self.keys_final = {}
        tags_final = self.create_final_get_tags_final()
        self.final = KeymapStructure.KeymapStructure(
            name=self.name,
            field=self.field,
            keys=self.keys_final,
            measure_length=self.measure_length,
            normalizer=self.create_final_get_final_normalizers(),
            print_all=self.print_all,
            tags=tags_final,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        for key in self.keys:
            self.keys_final.update(key.get_subcomponent_final())

    def finalize_finals(self) -> None:
        assert self.final is not None
        self.final.finalize()
