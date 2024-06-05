import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.FieldListField as FieldListField
import Structure.Importer.Field.KeymapImportField as KeymapImportField
import Structure.Importer.Field.KeymapKeyField as KeymapKeyField
import Structure.Importer.Field.NormalizerListField as NormalizerListField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.StructureComponent as StructureComponent
import Structure.KeymapStructure as KeymapStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class KeymapComponent(StructureComponent.StructureComponent[KeymapStructure.KeymapStructure]):

    class_name_article = "a Keymap"
    class_name = "Keymap"
    my_type = [dict]
    my_capabilities = Capabilities.Capabilities(has_importable_keys=True, has_keys=True, is_structure=True)
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
            TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        ), "a dict", "a str", "a dict")),
    )

    def __init__(self, data:ComponentTyping.KeymapComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.field = data.get("field", "field")
        self.measure_length = data.get("measure_length", False)
        self.print_all = data.get("print_all", False)

        self.import_field = KeymapImportField.KeymapImportField(data.get("imports", []), ["imports"])
        self.keys = FieldListField.FieldListField([KeymapKeyField.KeymapKeyField(data=key_data, key=key, tag_set=self.children_tags, path=["keys", key]) for key, key_data in data["keys"].items()], ["keys"])
        self.normalizer_field:NormalizerListField.NormalizerListField = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.tags_for_all_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.tags_for_all_field.add_to_tag_set(self.children_tags)
        self.import_field.import_into(self.keys)
        self.keys.for_each(lambda key: key.add_tag_fields(self.tags_for_all_field))
        self.fields.extend([self.import_field, self.tags_for_all_field, self.keys, self.normalizer_field])

    def create_final(self) -> None:
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
            keys_intermediate={key.key: key.get_subcomponent_final() for key in self.keys},
            normalizer=self.normalizer_field.get_finals(),
            tags={keymap_field.key: keymap_field.tags_field.get_finals() for keymap_field in self.keys}
        )

    def finalize(self) -> None:
        self.get_final().finalize()
