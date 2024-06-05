import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.NormalizerListField as NormalizerListField
import Structure.Importer.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.TypeField as TypeField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.VolumeStructure as VolumeStructure
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class VolumeComponent(AbstractGroupComponent.AbstractGroupComponent):

    class_name_article = "a Volume"
    class_name = "Volume"
    my_type = {tuple}
    my_capabilities = Capabilities.Capabilities(is_group=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("position_key", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("print_additional_data", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("state_key", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.VolumeTypedDict, name: str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.field = data.get("field", "block")
        self.position_key = data["position_key"]
        self.print_additional_data = data.get("print_additional_data", True)
        self.state_key = data["state_key"]
        self.children_has_normalizer = True # has to turn into tuple that the thing recognizes.
        self.final_structure:VolumeStructure.VolumeStructure|None=None
        self.my_type.add(tuple)

        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(data.get("subcomponent"), ["subcomponent"])
        self.normalizer_field:NormalizerListField.NormalizerListField = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.this_type_field = TypeField.TypeField(data["this_type"], ["this_type"])
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.fields.extend([self.subcomponent_field, self.normalizer_field, self.types_field, self.this_type_field, self.tags_field])

    def get_subcomponents(self) -> list[Component.Component]:
        subcomponent = self.subcomponent_field.get_component()
        return [] if subcomponent is None else [subcomponent]

    def create_final(self) -> None:
        self.final_structure = VolumeStructure.VolumeStructure(
            name=self.name,
            field=self.field,
            position_key=self.position_key,
            state_key=self.state_key,
            print_additional_data=self.print_additional_data,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )
        self.final = {}

    def get_final_structure(self) -> VolumeStructure.VolumeStructure:
        if self.final_structure is None:
            raise Exceptions.AttributeNoneError("final_structure", self)
        return self.final_structure

    def link_finals(self) -> None:
        super().link_finals()
        final_structure = self.get_final_structure()
        final = self.get_final()
        final_structure.link_substructures(
            structure=self.subcomponent_field.get_final(),
            normalizer=self.normalizer_field.get_finals(),
            tags=self.tags_field.get_finals()
        )
        final[tuple] = final_structure
        for my_type in self.this_type_field.get_types(): final[my_type] = final_structure
