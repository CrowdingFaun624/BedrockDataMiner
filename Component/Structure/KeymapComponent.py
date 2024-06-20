import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.FieldListField as FieldListField
import Component.Structure.Field.KeymapImportField as KeymapImportField
import Component.Structure.Field.KeymapKeyField as KeymapKeyField
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.KeymapStructure as KeymapStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class KeymapComponent(StructureComponent.StructureComponent[KeymapStructure.KeymapStructure]):

    class_name_article = "a Keymap"
    class_name = "Keymap"
    my_capabilities = Capabilities.Capabilities(has_importable_keys=True, has_keys=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("keys", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent, or None", False, (str, dict, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        ), "a dict", "a str", "a dict")),
    )

    def __init__(self, data:ComponentTyping.KeymapTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.field = data.get("field", "field")
        self.measure_length = data.get("measure_length", False)
        self.print_all = data.get("print_all", False)

        self.import_field = KeymapImportField.KeymapImportField(data.get("imports", []), ["imports"])
        self.keys = FieldListField.FieldListField([KeymapKeyField.KeymapKeyField(key_data, key, self.children_tags, ["keys", key], self) for key, key_data in data["keys"].items()], ["keys"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.tags_for_all_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "dict"), ["this_type"])
        self.tags_for_all_field.add_to_tag_set(self.children_tags)
        self.keys.for_each(lambda key: key.add_tag_fields(self.tags_for_all_field))
        self.import_field.import_into(self.keys)
        self.this_type_field.must_be(StructureComponent.MAPPING_TYPES)
        self.fields.extend([self.import_field, self.tags_for_all_field, self.keys, self.this_type_field, self.normalizer_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = KeymapStructure.KeymapStructure(
            name=self.name,
            field=self.field,
            measure_length=self.measure_length,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_substructures(
            keys={key.key: key.get_subcomponent() for key in self.keys},
            key_types={key.key: tuple(key.get_types()) for key in self.keys},
            normalizer=self.normalizer_field.get_finals(),
            tags={keymap_field.key: keymap_field.tags_field.get_finals() for keymap_field in self.keys},
            keys_with_normalizers=[key.key for key in self.keys if (subcomponent := key.get_subcomponent()) is not None and subcomponent.children_has_normalizer] if self.children_has_normalizer else [],
        )
        self.my_type = set(self.this_type_field.get_types())
